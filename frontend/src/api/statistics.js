import request from '@/utils/axios_api_client_setup'

// 获取用户台账统计
export function getLedgerStatsByUser(params) {
  return request({
    url: '/meta/stats/ledger_by_user',
    method: 'get',
    params
  })
} 