<template>
  <div class="app-container">
    <el-container>
      <el-header height="60px">
        <h1>股票交易系统</h1>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical-demo"
            @select="handleMenuSelect"
          >
            <el-menu-item index="data">
              <el-icon><DataAnalysis /></el-icon>
              <span>涨停数据</span>
            </el-menu-item>
            <el-menu-item index="tenDayTop30">
              <el-icon><Top /></el-icon>
              <span>10日涨幅榜</span>
            </el-menu-item>
            <el-menu-item index="concept">
              <el-icon><TrendCharts /></el-icon>
              <span>板块分析</span>
            </el-menu-item>
            <el-menu-item index="import">
              <el-icon><Upload /></el-icon>
              <span>手动导入</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <!-- 数据展示部分 -->
          <div v-if="activeMenu === 'data'">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>涨停数据</span>
                  <el-date-picker
                    v-model="selectedDate"
                    type="date"
                    placeholder="选择日期"
                    @change="fetchLimitUpData"
                  />
                </div>
              </template>
              <div v-if="loading" class="loading-container">
                <el-loading :fullscreen="false" text="加载中..." />
              </div>
              <div v-else-if="error" class="error-message">
                {{ error }}
              </div>
              <div v-else-if="Object.keys(limitUpData).length === 0" class="empty-message">
                暂无数据
              </div>
              <div v-else class="data-container">
                <el-collapse v-model="activeThemes">
                  <el-collapse-item
                    v-for="(stocks, theme) in limitUpData"
                    :key="theme"
                    :title="`${theme} (${stocks.length}只)`"
                  >
                    <el-table :data="stocks" style="width: 100%">
                      <el-table-column prop="code" label="股票代码" width="120" />
                      <el-table-column prop="name" label="股票名称" width="150" />
                      <el-table-column prop="date" label="日期" />
                      <el-table-column prop="price" label="价格" />
                      <el-table-column prop="change_percent" label="涨幅" />
                    </el-table>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-card>
          </div>
          
          <!-- 10日涨幅榜部分 -->
          <div v-if="activeMenu === 'tenDayTop30'">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>10日累计涨幅前30</span>
                  <el-date-picker
                    v-model="tenDayDate"
                    type="date"
                    placeholder="选择日期"
                    @change="fetchTenDayTop30"
                  />
                </div>
              </template>
              <div v-if="tenDayLoading" class="loading-container">
                <el-loading :fullscreen="false" text="加载中..." />
              </div>
              <div v-else-if="tenDayError" class="error-message">
                {{ tenDayError }}
              </div>
              <div v-else-if="tenDayData.length === 0" class="empty-message">
                暂无数据
              </div>
              <div v-else class="data-container">
                <el-table :data="tenDayData" style="width: 100%">
                  <el-table-column type="index" label="排名" width="80" />
                  <el-table-column prop="symbol" label="股票代码" width="120" />
                  <el-table-column prop="name" label="股票名称" width="150" />
                  <el-table-column prop="industry" label="概念" width="120" />
                  <el-table-column prop="ten_day_change" label="10日涨幅(%)" width="120" />
                  <el-table-column prop="daily_change" label="单日涨幅(%)" width="120" />
                </el-table>
              </div>
            </el-card>
          </div>
          
          <!-- 板块分析部分 -->
          <div v-if="activeMenu === 'concept'">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>板块分析</span>
                  <div class="header-controls">
                    <el-button type="primary" @click="refreshConceptData" :loading="conceptRefreshing">
                      <el-icon><Refresh /></el-icon>
                      同步当日板块数据
                    </el-button>
                    <el-radio-group v-model="conceptDays" @change="fetchConceptData">
                      <el-radio-button :label="2">2日</el-radio-button>
                      <el-radio-button :label="3">3日</el-radio-button>
                      <el-radio-button :label="4">4日</el-radio-button>
                      <el-radio-button :label="5">5日</el-radio-button>
                      <el-radio-button :label="10">10日</el-radio-button>
                    </el-radio-group>
                  </div>
                </div>
              </template>
              <div v-if="conceptLoading" class="loading-container">
                <el-loading :fullscreen="false" text="加载中..." />
              </div>
              <div v-else-if="conceptError" class="error-message">
                {{ conceptError }}
              </div>
              <div v-else-if="conceptData.length === 0" class="empty-message">
                暂无板块数据，请先点击"同步当日板块数据"
              </div>
              <div v-else class="data-container">
                <el-table :data="conceptData" style="width: 100%">
                  <el-table-column type="index" label="排名" width="80" />
                  <el-table-column prop="concept_code" label="板块代码" width="120" />
                  <el-table-column prop="concept_name" label="板块名称" width="200" />
                  <el-table-column 
                    prop="cumulative_change" 
                    :label="`${conceptDays}日累计涨幅(%)`" 
                    width="180"
                  >
                    <template #default="scope">
                      <span :style="{ color: scope.row.cumulative_change >= 0 ? '#f56c6c' : '#67c23a', fontWeight: '600' }">
                        {{ scope.row.cumulative_change.toFixed(2) }}
                      </span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-card>
          </div>
          
          <!-- 手动导入部分 -->
          <div v-if="activeMenu === 'import'">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>手动导入涨停数据</span>
                </div>
              </template>
              <el-form :model="importForm" label-width="80px">
                <el-form-item label="题材">
                  <el-input v-model="importForm.theme" placeholder="请输入题材名称" />
                </el-form-item>
                <el-form-item label="上传图片">
                  <el-upload
                    class="upload-demo"
                    action=""
                    :auto-upload="false"
                    :on-change="handleFileChange"
                    :limit="1"
                    :file-list="fileList"
                  >
                    <el-button type="primary">
                      <el-icon><Upload /></el-icon>
                      选择图片
                    </el-button>
                    <template #tip>
                      <div class="el-upload__tip">
                        请上传包含涨停股票数据的图片
                      </div>
                    </template>
                  </el-upload>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="submitImport" :loading="importLoading">
                    提交导入
                  </el-button>
                </el-form-item>
              </el-form>
              <div v-if="importMessage" class="import-message">
                {{ importMessage }}
              </div>
            </el-card>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const activeMenu = ref('data')
    const selectedDate = ref('')
    const limitUpData = ref({})
    const loading = ref(false)
    const error = ref('')
    const activeThemes = ref([])
    const importForm = ref({ theme: '' })
    const fileList = ref([])
    const importLoading = ref(false)
    const importMessage = ref('')
    
    // 10日涨幅榜相关
    const tenDayDate = ref('2026-04-08')
    const tenDayData = ref([])
    const tenDayLoading = ref(false)
    const tenDayError = ref('')
    
    // 板块分析相关
    const conceptDays = ref(10)
    const conceptData = ref([])
    const conceptLoading = ref(false)
    const conceptError = ref('')
    const conceptRefreshing = ref(false)
    
    // 处理菜单选择
    const handleMenuSelect = (key) => {
      activeMenu.value = key
      
      // 切换到10日涨幅榜时自动加载数据
      if (key === 'tenDayTop30') {
        fetchTenDayTop30()
      }
      
      // 切换到板块分析时自动加载数据
      if (key === 'concept') {
        fetchConceptData()
      }
    }
    
    // 获取涨停数据
    const fetchLimitUpData = async () => {
      loading.value = true
      error.value = ''
      try {
        const params = selectedDate.value ? { date: selectedDate.value } : {}
        const response = await axios.get('http://localhost:8000/api/limit-up', { params })
        if (response.data.success) {
          limitUpData.value = response.data.data
          // 展开所有题材
          activeThemes.value = Object.keys(response.data.data)
        } else {
          error.value = response.data.message
        }
      } catch (err) {
        error.value = '获取数据失败，请稍后重试'
        console.error(err)
      } finally {
        loading.value = false
      }
    }
    
    // 获取10日涨幅榜数据
    const fetchTenDayTop30 = async () => {
      tenDayLoading.value = true
      tenDayError.value = ''
      try {
        let params = {}
        if (tenDayDate.value) {
          // 格式化日期为YYYYMMDD格式
          const date = new Date(tenDayDate.value)
          const year = date.getFullYear()
          const month = String(date.getMonth() + 1).padStart(2, '0')
          const day = String(date.getDate()).padStart(2, '0')
          const formattedDate = `${year}${month}${day}`
          params.target_date = formattedDate
          console.log('请求日期:', formattedDate)
        }
        const response = await axios.get('http://localhost:8000/api/tushare/ten-day-top30', { params })
        console.log('API响应:', response.data)
        if (response.data.success) {
          tenDayData.value = response.data.data
          console.log('数据长度:', response.data.data.length)
          console.log('前3条数据:', response.data.data.slice(0, 3))
        } else {
          tenDayError.value = response.data.message
        }
      } catch (err) {
        tenDayError.value = '获取数据失败，请稍后重试'
        console.error('错误:', err)
      } finally {
        tenDayLoading.value = false
      }
    }
    
    // 获取板块分析数据
    const fetchConceptData = async () => {
      conceptLoading.value = true
      conceptError.value = ''
      try {
        const response = await axios.get('http://localhost:8000/api/concept/data', { 
          params: { days: conceptDays.value } 
        })
        if (response.data.success) {
          conceptData.value = response.data.data
        } else {
          conceptError.value = response.data.message
        }
      } catch (err) {
        conceptError.value = '获取数据失败，请稍后重试'
        console.error(err)
      } finally {
        conceptLoading.value = false
      }
    }
    
    // 刷新板块数据
    const refreshConceptData = async () => {
      conceptRefreshing.value = true
      conceptError.value = ''
      try {
        const response = await axios.get('http://localhost:8000/api/concept/refresh')
        if (response.data.success) {
          // 刷新成功后重新加载数据
          await fetchConceptData()
        } else {
          conceptError.value = response.data.message
        }
      } catch (err) {
        conceptError.value = '同步数据失败，请稍后重试'
        console.error(err)
      } finally {
        conceptRefreshing.value = false
      }
    }
    
    // 处理文件上传
    const handleFileChange = (file) => {
      fileList.value = [file]
    }
    
    // 提交导入
    const submitImport = async () => {
      if (!importForm.value.theme) {
        importMessage.value = '请输入题材名称'
        return
      }
      if (fileList.value.length === 0) {
        importMessage.value = '请选择图片'
        return
      }
      
      importLoading.value = true
      importMessage.value = ''
      
      try {
        const formData = new FormData()
        formData.append('file', fileList.value[0].raw)
        formData.append('theme', importForm.value.theme)
        
        const response = await axios.post('/api/ocr/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (response.data.success) {
          importMessage.value = '导入成功'
          // 清空表单
          importForm.value.theme = ''
          fileList.value = []
          // 刷新数据
          if (activeMenu.value === 'data') {
            fetchLimitUpData()
          }
        } else {
          importMessage.value = response.data.message
        }
      } catch (err) {
        importMessage.value = '导入失败，请稍后重试'
        console.error(err)
      } finally {
        importLoading.value = false
      }
    }
    
    // 初始化
    onMounted(() => {
      fetchLimitUpData()
    })
    
    return {
      activeMenu,
      selectedDate,
      limitUpData,
      loading,
      error,
      activeThemes,
      importForm,
      fileList,
      importLoading,
      importMessage,
      tenDayDate,
      tenDayData,
      tenDayLoading,
      tenDayError,
      conceptDays,
      conceptData,
      conceptLoading,
      conceptError,
      conceptRefreshing,
      handleMenuSelect,
      fetchLimitUpData,
      fetchTenDayTop30,
      fetchConceptData,
      refreshConceptData,
      handleFileChange,
      submitImport
    }
  }
}
</script>

<style>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  padding-left: 20px;
}

.el-header h1 {
  margin: 0;
  font-size: 20px;
}

.el-menu-vertical-demo {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.loading-container {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-message {
  color: red;
  text-align: center;
  padding: 20px;
}

.empty-message {
  text-align: center;
  padding: 40px;
  color: #999;
}

.import-message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
  background-color: #f0f9eb;
  color: #67c23a;
}

.import-message.error {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
