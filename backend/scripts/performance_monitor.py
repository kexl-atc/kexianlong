#!/usr/bin/env python
"""
性能监控脚本
监控API响应时间和系统资源使用
"""
import time
import requests
import psutil
import json
from datetime import datetime
from statistics import mean

# 配置
API_ENDPOINTS = [
    '/api/login',
    '/api/ledger',
    '/api/provinces'
]
BASE_URL = 'http://localhost:5000'
MONITOR_DURATION = 60  # 监控持续时间（秒）
SAMPLE_INTERVAL = 5    # 采样间隔（秒）

class PerformanceMonitor:
    def __init__(self):
        self.results = {
            'api_response_times': {},
            'system_metrics': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
    
    def test_api_endpoint(self, endpoint):
        """测试API端点响应时间"""
        url = BASE_URL + endpoint
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code < 400
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': -1,
                'success': False,
                'error': str(e)
            }
    
    def collect_system_metrics(self):
        """收集系统指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 获取进程信息
        process_info = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            if 'python' in proc.info['name'].lower() or 'node' in proc.info['name'].lower():
                process_info.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_mb': memory.used / (1024 * 1024),
            'disk_percent': disk.percent,
            'processes': process_info
        }
    
    def run(self):
        """运行监控"""
        print(f"开始性能监控，持续 {MONITOR_DURATION} 秒...")
        
        start_time = time.time()
        sample_count = 0
        
        # 初始化API响应时间记录
        for endpoint in API_ENDPOINTS:
            self.results['api_response_times'][endpoint] = []
        
        while time.time() - start_time < MONITOR_DURATION:
            sample_count += 1
            print(f"\n采样 #{sample_count}")
            
            # 测试API端点
            for endpoint in API_ENDPOINTS:
                result = self.test_api_endpoint(endpoint)
                self.results['api_response_times'][endpoint].append(result)
                
                if result['success']:
                    print(f"  {endpoint}: {result['response_time']:.2f}ms")
                else:
                    print(f"  {endpoint}: 失败 - {result.get('error', 'Unknown error')}")
            
            # 收集系统指标
            metrics = self.collect_system_metrics()
            self.results['system_metrics'].append(metrics)
            print(f"  CPU: {metrics['cpu_percent']}%, 内存: {metrics['memory_percent']}%")
            
            # 等待下一次采样
            time.sleep(SAMPLE_INTERVAL)
        
        self.results['end_time'] = datetime.now().isoformat()
        self.analyze_results()
    
    def analyze_results(self):
        """分析监控结果"""
        print("\n" + "="*50)
        print("性能监控报告")
        print("="*50)
        
        # API性能分析
        print("\nAPI性能统计:")
        for endpoint, results in self.results['api_response_times'].items():
            success_results = [r for r in results if r['success']]
            if success_results:
                response_times = [r['response_time'] for r in success_results]
                avg_time = mean(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                success_rate = (len(success_results) / len(results)) * 100
                
                print(f"\n{endpoint}:")
                print(f"  平均响应时间: {avg_time:.2f}ms")
                print(f"  最大响应时间: {max_time:.2f}ms")
                print(f"  最小响应时间: {min_time:.2f}ms")
                print(f"  成功率: {success_rate:.1f}%")
        
        # 系统资源分析
        print("\n系统资源使用统计:")
        cpu_values = [m['cpu_percent'] for m in self.results['system_metrics']]
        memory_values = [m['memory_percent'] for m in self.results['system_metrics']]
        
        print(f"  CPU使用率 - 平均: {mean(cpu_values):.1f}%, 最大: {max(cpu_values):.1f}%")
        print(f"  内存使用率 - 平均: {mean(memory_values):.1f}%, 最大: {max(memory_values):.1f}%")
        
        # 保存报告
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存到: {report_file}")

if __name__ == '__main__':
    monitor = PerformanceMonitor()
    monitor.run()