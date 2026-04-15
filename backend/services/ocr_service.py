import cv2
import pytesseract
from PIL import Image
import numpy as np
import re
from datetime import datetime

class OCRService:
    def __init__(self):
        # 配置Tesseract路径
        pytesseract.pytesseract.tesseract_cmd = r'e:\Users\luoch\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        pass
    
    def recognize_text(self, image_path):
        """
        识别图片中的文字
        :param image_path: 图片路径
        :return: 识别的文字
        """
        try:
            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                raise Exception("无法读取图片")
            
            # 预处理图片 - 提高识别准确率
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 增强对比度
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # 二值化 - 适用于表格
            binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # 去除表格线
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            processed = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # 尝试使用中文+英文识别
            try:
                text = pytesseract.image_to_string(processed, lang='chi_sim+eng', config='--psm 6')
            except Exception as e:
                print(f"中文识别失败，尝试仅使用英文: {str(e)}")
                # 备选方案：仅使用英文
                text = pytesseract.image_to_string(processed, lang='eng', config='--psm 6')
            
            return text
        except Exception as e:
            # 提供更详细的错误信息
            error_msg = f"识别失败: {str(e)}"
            print(f"OCR识别错误: {error_msg}")
            return error_msg
    
    def extract_stock_data(self, text):
        """
        从识别的文字中提取股票数据
        支持韭研公社等涨停复盘表格格式
        :param text: 识别的文字
        :return: 按题材分组的字典
        """
        result = {}
        lines = text.split('\n')
        
        current_theme = None
        current_stocks = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试识别题材行（通常包含 *数字 或 以中文开头且较短）
            theme_match = self._extract_theme(line)
            if theme_match:
                # 保存上一个题材的数据
                if current_theme and current_stocks:
                    result[current_theme] = current_stocks
                
                current_theme = theme_match
                current_stocks = []
                continue
            
            # 尝试识别股票行
            stock_info = self._extract_stock_line(line)
            if stock_info and current_theme:
                current_stocks.append(stock_info)
        
        # 保存最后一个题材的数据
        if current_theme and current_stocks:
            result[current_theme] = current_stocks
        
        return result
    
    def _extract_theme(self, line):
        """
        提取题材名称
        匹配模式：
        - 医疗医药*7
        - 美伊战争*6
        - 电力*4
        """
        # 清理行首的特殊字符
        line = re.sub(r'^[\s\|\-]+', '', line)
        
        # 匹配题材名称（中文+可能的数字标记）
        # 模式：中文题材名 + *数字 或 纯中文题材名
        patterns = [
            r'^([\u4e00-\u9fa5]+)[\*×]\d+',  # 匹配 "医疗医药*7" 或 "医疗医药×7"
            r'^([\u4e00-\u9fa5]{2,10})[^\u4e00-\u9fa5]',  # 匹配2-10个中文开头的
            r'^([\u4e00-\u9fa5]{2,10})$',  # 匹配纯中文题材名
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                theme = match.group(1)
                # 过滤掉非题材的行
                if self._is_valid_theme(theme):
                    return theme
        
        return None
    
    def _is_valid_theme(self, text):
        """
        判断是否是有效的题材名称
        """
        # 排除常见的非题材词汇
        invalid_keywords = ['板数', '代码', '个股', '涨停', '时间', '流通', '市值', 
                           '成交额', '关键词', '不含', '统计', '数据', '根据', '市场',
                           '信息', '综合', '人工', '编写', '全网', '查看', '详细']
        
        for keyword in invalid_keywords:
            if keyword in text:
                return False
        
        return True
    
    def _extract_date(self, text):
        """
        从识别的文字中提取日期
        匹配模式：
        - 2024-04-01
        - 2024/04/01
        - 2024年4月1日
        - 04-01 周一
        """
        # 日期模式
        date_patterns = [
            r'(\d{4})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])',  # 2024-04-01 或 2024/04/01
            r'(\d{4})年(0?[1-9]|1[0-2])月(0?[1-9]|[12]\d|3[01])日',  # 2024年4月1日
            r'(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])',  # 04-01 或 04/01
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if len(match) == 3:
                        # 完整日期格式 (2024-04-01 或 2024年4月1日)
                        year, month, day = match
                        try:
                            # 构建日期对象
                            date_obj = datetime(int(year), int(month), int(day))
                            return date_obj.date()
                        except:
                            continue
                    elif len(match) == 2:
                        # 月日格式 (04-01)
                        month, day = match
                        try:
                            # 使用当前年份
                            year = datetime.now().year
                            date_obj = datetime(year, int(month), int(day))
                            return date_obj.date()
                        except:
                            continue
        
        return None
    
    def _extract_stock_line(self, line):
        """
        从行中提取股票信息
        匹配模式：
        - 5天5板 600488 津药药业 9:25:00 69.2 0.9 创新药+...
        - 1 603222 济民健康 13:35:47 53.3 4.7 创新药+...
        """
        # 清理行首的特殊字符
        line = re.sub(r'^[\s\|\-]+', '', line)
        
        # 匹配股票代码模式 (6位数字，可能没有市场标识)
        code_pattern = r'(\d{6})'
        code_match = re.search(code_pattern, line)
        
        if not code_match:
            return None
        
        code = code_match.group(1)
        # 根据股票代码判断市场
        market = self._determine_market(code)
        
        # 提取股票名称（通常在代码后面）
        # 分割行，找到代码位置
        parts = line.split()
        name = None
        
        for i, part in enumerate(parts):
            if code in part:
                # 股票名称通常在代码后面
                if i + 1 < len(parts):
                    name = parts[i + 1]
                    # 过滤掉时间格式的名称和纯数字
                    if ':' in name or name.isdigit():
                        name = None
                break
        
        # 如果找不到名称，使用代码作为名称
        if not name:
            name = code
        
        return {
            'code': code,
            'market': market,
            'name': name
        }
    
    def _determine_market(self, code):
        """
        根据股票代码判断市场
        - 6开头：沪市
        - 0开头：深市
        - 3开头：创业板
        - 9开头：北交所
        """
        if code.startswith('6'):
            return 'SH'
        elif code.startswith('0'):
            return 'SZ'
        elif code.startswith('3'):
            return 'SZ'
        elif code.startswith('9'):
            return 'BJ'
        else:
            return 'SH'  # 默认沪市
    
    def process_image(self, image_path):
        """
        处理图片并返回结构化数据
        :param image_path: 图片路径
        :return: 按题材分组的股票数据和识别到的日期
        """
        text = self.recognize_text(image_path)
        
        if text.startswith('识别失败'):
            return {'error': text}
        
        # 清理和规范化文本
        text = self._clean_text(text)
        
        data = self.extract_stock_data(text)
        date = self._extract_date(text)
        
        return {
            'success': True,
            'data': data,
            'date': date.isoformat() if date else None,
            'raw_text': text  # 返回原始识别文本，便于调试
        }
    
    def _clean_text(self, text):
        """
        清理和规范化识别的文本
        :param text: 识别的原始文本
        :return: 清理后的文本
        """
        # 移除乱码字符
        import re
        # 保留中文字符、数字、英文字母和常见标点
        cleaned = re.sub(r'[^一-龥0-9a-zA-Z\s.,，。:：;；()（）]', '', text)
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned
