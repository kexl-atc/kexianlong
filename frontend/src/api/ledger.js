import request from '@/utils/axios_api_client_setup'

// 获取台账列表
export function getLedgerList(params) {
  return request({
    url: '/ledger',
    method: 'get',
    params
  })
}

// 获取单个台账详情
export function getLedgerEntry(id) {
  return request({
    url: `/ledger/${id}`,
    method: 'get'
  })
}

// 创建台账
export function createLedgerEntry(data) {
  return request({
    url: '/ledger',
    method: 'post',
    data
  })
}

// 更新台账
export function updateLedgerEntry(id, data) {
  return request({
    url: `/ledger/${id}`,
    method: 'put',
    data
  })
}

// 删除台账
export function deleteLedgerEntry(id) {
  return request({
    url: `/ledger/${id}`,
    method: 'delete'
  })
}

// 获取省份列表
export function getProvinces() {
  return request({
    url: '/provinces',
    method: 'get'
  })
}

// 获取性质选项
export function getNatureOptions() {
  return request({
    url: '/nature-options',
    method: 'get'
  })
}

// 获取项目搜索建议
export function getProjectSuggestions(query) {
  return request({
    url: '/suggestions/project_items',
    method: 'get',
    params: { query }
  })
}

// 导出台账数据
export function exportLedger(params) {
  return request({
    url: '/meta/export/ledger',
    method: 'get',
    params,
    responseType: 'blob'
  })
}