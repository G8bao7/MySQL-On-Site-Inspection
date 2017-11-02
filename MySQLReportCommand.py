#encoding=utf8

class Report(object):

    def __init__(self):
        pass

    def setup(self,metrics):
        self.metrics=metrics
    

    def report(self):
        '''
        给出报告
        '''
        pass

def near(value,near_value,percent):
    value=long(value)
    near_value=long(near_value)
    # 如果 value 与 near value 差距不超过 percent，则认为仍然相等
    return value > near_value*(100.0-percent)/100 and value < near_value*(100.0+percent)/100 


def performacne_innodb_pool_cal(metrics,variable_name,variable_value):
    # 这个函数根据给定的机器可用内存，计算合适的 innodb 参数大小出来
    # 主要的参考计算方法为：
    # 70%的可用内存向下取整后得到可用的 GB 值，用于 InnoDB buffer pool
    # 根据每个 GB 一个 instance，指定 pool instance
    # chunck size 采用128MB 作为参考值
    # IO 相关如下：
    # 如果是 SSD：
    # io cap 设置为3000:5000
    # HDD：
    # io cap 设置为 700:1200
    # io 线程数量等于 数据库可用内存数量
    # 所有尺寸允许20的误差
    cpus=metrics['resource']['cpus']
    mems=metrics['resource']['mems']
    storage_type=metrics['resource']['storage_type']
    variable_value=int(variable_value)

    if variable_name in ("innodb_read_io_threads","innodb_write_io_threads","innodb_purge_threads"):
        if int(variable_value)!=cpus:
            return cpus
        else:
            return None
    if variable_name in ("innodb_io_capacity","innodb_io_capacity_max"):
        dc={
            "SSD":{
                "innodb_io_capacity":3000,
                "innodb_io_capacity_max":5000,
            },
            "HDD":{
                'innodb_io_capacity':700,
                "innodb_io_capacity_max":1200
            }
        }
        if near(variable_value,dc[storage_type][variable_name],20):
            return None
        else:
            return dc[storage_type][variable_name]
    pool_size=int(mems*0.7)
    if variable_name=='innodb_buffer_pool_instances':
        if variable_value!=pool_size:
            return pool_size
        else:
            return None
    if variable_name=='innodb_log_buffer_size':
        if near(variable_value,pool_size*1024*1024*1024,20):
            return None
        else:
            return str(pool_size)+"G"
    if variable_name=='innodb_buffer_pool_chunk_size':
        # 128MB
        if variable_value!=134217728:
            return 134217728
        else:
            return None



class MySQLInstanceReport(Report):

    performance_advistor={

    }

    datasafe_advistor={
        'variables':{
            "autocommit":{
                'expression':'=',
                "value":"ON"
            },
            "auto_increment_increment":{
                "expression":'=',
                "value":"1",
            },
            "auto_increment_offset":{
                "expression":'=',
                "value":"1",
            },
            "big_tables":{
                "expression":'=',
                "value":"ON",
            },
            "binlog_checksum":{
                "expression":'=',
                "value":"NONE",
            },
            "binlog_format":{
                "expression":"=",
                "value":"ROW"
            },
            "binlog_row_image":{
                "expression":"=",
                "value":"FULL"
            },
            "binlog_rows_query_log_events":
            {
                "expression":"=",
                "value":"ON"
            },
            "character_set_client":{
                "expression":"in",
                "value":['utf8','utf8mb4']
            },
            "character_set_connection":{
                "expression":"in",
                "value":['utf8','utf8mb4']
            },
            "character_set_results":{
                "expression":"in",
                "value":['utf8','utf8mb4']
            },
            "character_set_server":{
                "expression":"in",
                "value":['utf8','utf8mb4']
            },
            "connect_timeout":{
                'expression':"range",
                "value":"10-60"
            },
            "default_storage_engine":{
                'expression':'=',
                "value":"InnoDB"
            },
            "enforce_gtid_consistency":{
                "expression":'=',
                "value":"ON"
            },
            "expire_logs_days":{
                "expression":"range",
                "value":"3-30"
            },
            "general_log":{
                "expression":"=",
                "value":"OFF"
            },
            "gtid_mode":{
                "expression":"=",
                "value":"ON"
            },
            "init_connect":{
                "expression":'not have',
                "value":''
            },
            "init_slave":{
                "expression":'not have',
                "value":''
            },
            'innodb_adaptive_flushing':{
                "expression":"=",
                "value":"ON"
            },
            "innodb_adaptive_hash_index":{
                "expression":"=",
                "value":"ON"
            },
            "innodb_read_io_threads":{
                "expression":'function',
                "value":performacne_innodb_pool_cal
            },
            "innodb_write_io_threads":{
                "expression":'function',
                "value":performacne_innodb_pool_cal
            },
            "innodb_purge_threads":{
                "expression":'function',
                "value":performacne_innodb_pool_cal
            },
            "innodb_io_capacity":{
                "expression":'function',
                "value":performacne_innodb_pool_cal
            },
            "innodb_buffer_pool_instances":{
                "expression":'function',
                "value":performacne_innodb_pool_cal
            },
            "innodb_log_buffer_size":{
                "expression":'function',
                "value":performacne_innodb_pool_cal
            },
            "innodb_buffer_pool_chunk_size":{
                "expression":'function',
                "value":performacne_innodb_pool_cal
            },
            "innodb_autoinc_lock_mode":{
                "expression":"=",
                "value":"2"
            },
            "innodb_change_buffering":{
                'expression':"=",
                "value":"all"
            },
            "innodb_checksum_algorithm":{
                "expression":'=',
                "value":"crc32"
            },
            "innodb_commit_concurrency":{
                "expression":"=",
                "value":'0'
            },
            "innodb_deadlock_detect":{
                "expression":'=',
                'value':'ON'
            },
            "innodb_doublewrite":{
                "expression":"=",
                "value":"ON"
            },
            "innodb_fast_shutdown":{
                "expression":"=",
                "value":"1"
            },
            "innodb_file_per_table":{
                "expression":"=",
                "value":'ON'
            },
            "innodb_flush_log_at_trx_commit":{
                "expression":"=",
                "value":"1"
            },
            "innodb_flush_method":{
                "expression":'in',
                "value":['O_DIRECT','fsync']
            },
            "innodb_force_recovery":{
                "expression":'=',
                "value":'0'
            },
            "innodb_large_prefix":{
                "expression":"=",
                "value":"ON"
            },
            "innodb_lock_wait_timeout":{
                "expression":'range',
                "value":'10-3600'
            },
            "innodb_log_file_size":{
                "expression":'near',
                "value":(2*1024*1024*1024,30)
            },
            "innodb_log_files_in_group":{
                "expression":'=',
                "value":'3'
            },
            "innodb_open_files":{
                "expression":"range",
                "value":"3000-8000"
            },
            "innodb_print_all_deadlocks":{
                "expression":"=",
                "value":"ON"
            },
            "innodb_rollback_on_timeout":{
                "expression":'=',
                "value":"OFF"
            },
            "innodb_strict_mode":{
                "expression":"=",
                "value":'ON'
            },
            "innodb_support_xa":{
                "expression":'=',
                "value":"ON"
            },
            "innodb_table_locks":{
                "expression":'=',
                "value":'ON'
            },
            "innodb_thread_concurrency":{
                "expression":'=',
                "value":'0'
            },
            'innodb_undo_log_truncate':{
                "expression":'=',
                "value":'ON'
            },
            "innodb_undo_logs":{
                "expression":'=',
                "value":'128'
            },
            'innodb_undo_tablespaces':{
                "expression":'range',
                "value":'16-64'
            },
            'innodb_use_native_aio':{
                'expression':'=',
                "value":'ON'
            },
            "interactive_timeout":{
                "expression":'range',
                "value":'30-28800'
            },
            "wait_timeout":{
                "expression":'range',
                "value":'30-28800'
            },
            "lock_wait_timeout":{
                "expression":'range',
                "value":'30-28800'
            },
            "log_bin":{
                "expression":'=',
                "value":'ON'
            },
            "log_bin_trust_function_creators":{
                "expression":"=",
                "value":"ON"
            },
            "log_slave_updates":{
                "expression":"=",
                "value":"ON"
            },
            "log_timestamps":{
                "expression":"=",
                "value":"UTC"
            },
            "long_query_time":{
                "expression":'range',
                "value":"0-10"
            },
            'lower_case_file_system':{
                "expression":'=',
                "value":"ON"
            },
            "lower_case_table_names":{
                "expression":'=',
                "value":'1'
            },
            "master_info_repository":{
                "expression":"=",
                "value":"TABLE"
            },
            "relay_log_info_repository":{
                "expression":'=',
                "value":'TABLE'
            },
            "max_allowed_packet":{
                "expression":"near",
                "value":(1*1024*1024*1024,50)
            },
            "max_binlog_size":{
                "expression":"near",
                "value":(1*1024*1024*1024,50)
            },
            "max_connections":{
                "expression":'range',
                "value":'1000-8000'
            },
            "max_execution_time":{
                "expression":'=',
                "value":"0"
            },
            "old_alter_table":{
                "expression":'=',
                "value":"OFF"
            },
            "old_passwords":{
                "expression":"=",
                "value":"0"
            },
            'performance_schema':{
                'expression':"=",
                "value":"ON"
            },
            "query_cache_type":{
                "expression":'=',
                "value":"OFF"
            },
            "read_only":{
                "expression":"masterslave",
                "value":{
                    "master":"OFF",
                    "slave":"ON"
                }
            },
            "super_read_only":{
                "expression":"masterslave",
                "value":{
                    "master":"OFF",
                    "slave":"ON"
                }
            },
            'tx_read_only':{
                "expression":"masterslave",
                "value":{
                    "master":"OFF",
                    "slave":"ON"
                }
            },
            "relay_log_purge":{
                "expression":'=',
                "value":"ON"
            },
            "report_host":{
                "expression":"have",
                "value":"hostname"
            },
            "server_id":{
                "expression":"have",
                'value':""
            },
            "server_uuid":{
                "expression":'have',
                "value":""
            },
            "skip_name_resolve":{
                "expression":"=",
                "value":"ON"
            },
            "slave_exec_mode":{
                "expression":"=",
                "value":"ON"
            },
            "slave_parallel_type":{
                "expression":"=",
                "value":"DATABASE"
            },
            "slave_skip_errors":{
                "expression":"=",
                "value":"OFF"
            },
            "slow_query_log":{
                "expression":"=",
                "value":"ON"
            },
            "sql_log_off":{
                "expression":"=",
                "value":"OFF"
            },
            "sql_mode":{
                'expression':"have",
                "value":['STRICT_TRANS_TABLES',]
            },
            "sql_safe_updates":{
                "expression":"=",
                "value":"="
            },
            "sync_binlog":{
                "expression":"=",
                "value":"1"
            },
            "tx_isolation":{
                "expression":"=",
                "value":"READ-COMMITTED"
            },

        }
    }

    def __init__(self,db_advistor):
        
        self.advistor=db_advistor


    def variable_advistor(self):
        # 检查并给出参数修改的建议
        #此处以后需要入库可编辑
        for k,v in self.variables:
            if k in self.advistor['variables']:
                # 这里的判断条件为：
                # = 指定值，如果不是，则认为失败
                # range,在某一个值范围内，如果不是，则失败 必定是 a-b 形式的 value
                # function 作为函数调用,传入 metric,如果存在建议，返回建议值，否则为 None，根据返回结果决定是否失败
                # in 多值列表，如果不在，则认为失败
                # not in 多值列表，如果存在，则认为失败
                # have 如果没有设置，则认为失败
                # not have 如果设置了，则认为失败
                if self.advistor['variables'][k]['expression']=='=':
                    if v.upper()!=self.advistor['variables'][k]['value'].upper():
                        yield {
                                "variable_name":k,
                                "current_value":v,
                                "advice_value":self.advistor['variables'][k]['value']
                            }
                elif self.advistor['variables'][k]['expression']=='range':
                    start,end=self.advistor['variables'][k]['value'].split('-')
                    start=long(start) if len(start)>0 else 0
                    end=long(end) if len(end)>0 else 0
                    if end==0:
                         if long(v) < start :
                             yield {
                                "variable_name":k,
                                "current_value":v,
                                "advice_value":self.advistor['variables'][k]['value']
                            }
                    else:
                        if long(v) < start or long(v)> end:
                            yield {
                                    "variable_name":k,
                                    "current_value":v,
                                    "advice_value":self.advistor['variables'][k]['value']
                                }
                elif self.advistor['variables'][k]['expression']=='near':
                    adv_value,near_percent=self.advistor['variables'][k]['value']
                    if not near(v,adv_value,30):
                        yield {
                                    "variable_name":k,
                                    "current_value":v,
                                    "advice_value":adv_value
                                }
                elif self.advistor['variables'][k]['expression']=='function':
                    advice=self.advistor['variables'][k]['value'](self.metric,k,v)
                    if advice:
                        yield {
                                "variable_name":k,
                                "current_value":v,
                                "advice_value":advice
                            }
                elif self.advistor['variables'][k]['expression']=='in':
                    values=v.split(',')
                    # 这里的逻辑是，如果有多值，则每个不在建议表的值会被单独报告
                    for value in values:
                        if value not in self.advistor['variables'][k]['value']:
                            yield {
                                "variable_name":k,
                                "current_value":v,
                                "failed_value":value,
                                "advice_value":self.advistor['variables'][k]['value']
                            }
                elif self.advistor['variables'][k]['expression']=='not in':
                    for value in values:
                        if value in self.advistor['variables'][k]['expression']:
                            yield {
                                "variable_name":k,
                                "current_value":v,
                                "failed_value":value,
                                "advice_value":self.advistor['variables'][k]['value']
                            }
                elif self.advistor['variables'][k]['expression']=='have':
                    if len(v)==0:
                        yield {
                                "variable_name":k,
                                "current_value":v,
                                "advice_value":self.advistor['variables'][k]['value']
                            }
                elif self.advistor['variables'][k]['expression']=='not have':
                    if len(v)!=0:
                        yield {
                                "variable_name":k,
                                "current_value":v,
                                "advice_value":''
                            }
                elif self.advistor['variables'][k]['expression']=='masterslave':
                    if self.is_master:
                        value=self.advistor['variables'][k]['value']['master']
                    else:
                        value=self.advistor['variables'][k]['value']['slave']
                    if v!=value:
                        yield {
                                "variable_name":k,
                                "current_value":v,
                                "advice_value":value
                            }
                    

    def status_advistor(self):
        #这部分主要根据带时间点的 status列表 
        # 检查假设为：
        # 运行线程数量 50%时间不超过 cpu 数量*2
        # 连接数量小于最大连接限制的70%
        # select+delete+update 的 SQL 数量，与 innodb rows read 的数量比例小于1：100000
        # 存在回滚事务
        # 存在 alter 语句执行
        # 存在 drop 执行
        # innodb 存在锁等待
        # Open_tables 达到innodb_open_files 50%以上
        # Qcache_hits占比小于总查询数量的10%
        # 存在 Aborted_connects Aborted_clients
        cpus=metrics['resource']['cpus']
        mems=metrics['resource']['mems']
        storage_type=metrics['resource']['storage_type']
        checked_status={}
        #轮询所有 status
        # 通用逻辑：
        # 1. 期间出现
        # 2. 期间表达式为真
        # 3. 期间表达式一定比例出现一定时间
        

        def run_less_cpu(pre_status,status,metric):
            if int(status['Threads_running'])>cpus*2:
                return "运行线程数量超过可用cpu两倍"
            return None
            
        def connected_less_max(pre_status,status):
            max_connection=self.variables['max_connections']*0.7
            if int(status['Threads_connected'])>max_connection:
                return "连接数达到最大连接限制的70%以上"
            return None
        
        def open_tables(pre_status,status):
            innodb_open_files=self.variables['innodb_open_files']*0.5
            if int(status['Open_tables'])>innodb_open_files:
                return "打开的表数量达到最大限制的50%以上"
            return None

        def qc_check(pre_status,status):
            select=status['Com_select']-pre_status['Com_select']
            qc=status['Qcache_hits']-pre_status['Qcache_hits']
            if qc*10<(qc+select):
                return "Query cache 命中数量低于总查询数量的十分之一"
            return None

        def innodb_read_by_sql(pre_status,status):
            sql_metrics=['Com_select',"Com_delete",'Com_update']
            innodb_metrics=['Innodb_rows_read',]
            sqls=sum([int(status[k]) for k in sql_metrics])-sum([int(pre_status[k]) for k in sql_metrics])
            rows=sum([int(status[k]) for k in innodb_metrics])-sum([int(pre_status[k]) for k in innodb_metrics])
            if sqls*100000< rows:
                return "平均每条 SQL 查询使用innodb 行数超过10万，需要优化"
            return None
            
        def innodb_rollback(pre_status,status):
            Handler_rollback=int(status['Handler_rollback'])-int(pre_status['Handler_rollback'])
            if Handler_rollback>0:
                return {
                "value":Handler_rollback,
                "message":"实例存在回滚 {0} 个"
                }
            else:
                return None
        
        def mysql_alter(pre_status,status):
            Com_alter_table=int(status['Com_alter_table'])-int(pre_status['Com_alter_table'])
            if Com_alter_table>0:
                return {
                "value":Com_alter_table,
                "message":"实例alter table {0} 个"
                }
            else:
                return None
            
        def mysql_drop(pre_status,status):
            drop_metrics=["Com_drop_db",'Com_drop_index','Com_drop_table','Com_drop_trigger']
            drops=sum([int(status[k]) for k in drop_metrics])-sum([int(pre_status[k]) for k in drop_metrics])
            if drops>0:
                return {
                "value":drops,
                "message":"实例发生 drop（库，表，索引，触发器） 行为 {0} 个"
                }
            else:
                return None

        def connection_abort(pre_status,status):
            abort_metrics=["Aborted_connects",'Aborted_clients']
            aborts=sum([int(status[k]) for k in abort_metrics])-sum([int(pre_status[k]) for k in abort_metrics])
            if aborts>0:
                return {
                "value":aborts,
                "message":"实例发生 连接失败 行为 {0} 个，请检查网络状况，以及数据库网络环境"
                }
            else:
                return None
        
        def innodb_wait_lock(pre_status,status):
            if status['Innodb_row_lock_current_waits']>0:
                return "InnoDB 存在锁等待"
            return None

        hit_status={
            "thread_running":{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"none",
                "function":run_less_cpu,
                "result":"percent",
                "value":50,
                "message":''
            },
            "thread_connected":{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"none",
                "function":connected_less_max,
                "result":"percent",
                "value":50,
                "message":''
            },
            "innodb_rollback":{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"sum",
                "function":innodb_rollback,
                "result":"have",
                "value":0,
                "message":''
            },
            "alter_table":{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"sum",
                "function":mysql_alter,
                "result":"have",
                "value":0,
                "message":''
            },
            "mysql_drop":{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"sum",
                "function":mysql_drop,
                "result":"have",
                "value":0,
                "message":''
            },
            "innodb_wait_lock":{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"none",
                "function":innodb_wait_lock,
                "result":"percent",
                "value":50,
                "message":''
            },
            "query_hits":{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"none",
                "function":qc_check,
                "result":"percent",
                "value":50,
                "message":''
            },
            'connection_abort':{
                "hit":0,# 命中时间数量
                "sum":0,# metric 列表
                "sum_method":"sum",
                "function":connection_abort,
                "result":"have",
                "value":0,
                "message":''
            }
        }
        pre_status=None
        for ctime,status in self.status:
            if pre_status is None:
                pre_status=status
                continue
            for k,v in hit_status.items():
                if v['sum_method']=='none':
                    message= v['function'](pre_status,status)
                    if message:
                        v['hit']+=1
                        v['message']=message
                elif v['sum_method']=='sum':
                    message= v['function'](pre_status,status)
                    if message:
                        v['hit']+=1
                        v['sum']+=message['value']
                        v['message']=message['message'].foramt(v['sum'])
            pre_status=status
        for k,v in hit_status.items():
            if v['result']=='percent':
                if v["hit"]/len(self.status)*100>v['value']:
                    yield {
                        "status":k,
                        "message":"超过{percent}%时间，{message}".format(**v)
                    }
            elif v['result']=='have':
                if v['sum']>0:
                    yield {
                        "status":k,
                        "message":"{message}".format(**v)
                    }


    def host_advistor(self):
        # CPU利用在50%时间以上小于50%
        # CPU wait 超过10%
        # CPU 中至少一颗的软中断超过50%
        # 进程 CPU 使用率占机器 CPU 使用率50%以下 TODO 暂时不关心
        # 进程内存使用率占机器已经使用量50%以下 TODO 暂时不关心
        # mem，峰值为可用总内存85%以下
        # swap 大于1G
        # 数据盘容量小于70%
        # 其他分区小于80%
        # 数据盘 io 利用率低于90%
        # io 调度算法为 deadline
        # TODO 以下为还需要加但没有加入的
        # mysql 进程 ulimit
        #  mysql 数据目录权限
        # mysql 用户不能为 root
        
        data_mount=self.metrics['instance']['mounted_dir']
        data_device=self.metrics['instance']['data_device']
        cpus=metrics['resource']['cpus']
        mems=metrics['resource']['mems']
        storage_type=metrics['resource']['storage_type']
        # 容量判断直接使用最末尾数据
        # 受制于采集手段，所有操作系统层面的状态，只能单线处理
        # CPU:mpstat
        # 进程：pidstat
        # 容量：df
        # io 利用率：iostat
        # 内存 /proc/meminfo
        # 调度算法 /
        df_status=self.host_status['df'][-1]
        for k,v in df_status.items():
            if k==data_mount:
                if v['use_percent']>70:
                    yield {
                        "host_status":"data_dir_used",
                        "message":"data dir {0}({1}%) more than 70%".format(k,v['use_percent'])
                    }
            else:
                if v['use_percent']>80:
                    yield {
                        "host_status":"dir_used",
                        "message":"dir {0}({1}) more than 80%".format(k,v['use_percent'])
                    }

        def cpu_percent(cpu_status):
            cpu_percent=100-cpu_status['ALL']['idle']
            if cpu_percent>50:
                return "CPU 使用率超过50%"
            return None
        
        def cpu_wait_percent(host_status):
            for cpu in cpu_status:
                if cpu!='ALL':
                    if cpu['io_wait']>10:
                        return "CPU io wait 超过10%"
        def cpu_irq(host_status):
            for cpu in cpu_status:
                if cpu!='ALL':
                    if cpu['soft']>50:
                        return "CPU 软中断超过50%"

        # cpu 相关
        cpu_status_assert={
            "cpu_percent":{
                'function':cpu_percent,
                "hit":0,
                "message":"",
                "hit_percent":50
            },
            "cpu_wait_percent":{
                'function':cpu_wait_percent,
                "hit":0,
                "message":"",
                "hit_percent":50
            },
            "cpu_irq":{
                'function':cpu_irq,
                "hit":0,
                "message":"",
                "hit_percent":50
            },
        }
        def process_assert(status_name,status_assert):
            for cpu_status in self.host_status[status_name]:
                for k,v in status_assert.items():
                    message= v['function'](cpu_status)
                    if message:
                        v['hit']+=1
                        v['message']=message
            for k, v in status_assert.items():
                if v['hit']*100/len(self.host_status[status_name])>v['hit_percent']:
                    yield {
                        'host_status':k,
                        'message':v['message']
                    }
        for result in process_assert('mpstat',cpu_status_assert):
            yield result
        
        def mem_used(mem_status):
            if (mem_status['MemTotal']-mem_status['MemAvailable'])*100/mem_status['MemTotal']>85:
                return '内存使用率大于85%'
            return None
        
        def swap_used(mem_status):
            if (mem_status['SwapTotal']-mem_status['SwapFree'])/1024/1024>1:
                return "swap 使用超过1GB"
            return None

        mem_status_assert={
            "mem_used":{
                'function':mem_used,
                'hit':0,
                'message':'',
                'hit_percent':50
            },
            'swap_used':{
                'function':swap_used,
                'hit':0,
                'message':'',
                'hit_percent':50
            }
        }
        for result in process_assert('meminfo',mem_status_assert):
            yield result
        

        def io_percent(io_status):
            for device,io in io_status.items():
                if device==data_device:
                    if io['percent']>80:
                        return "IO 利用率大于80%"
            return None

        io_status_assert={
            'io_percent':{
                'function':io_percent,
                'hit':0,
                'message':'',
                'hit_percent':50
            }
        }
        for result in process_assert('iostatus',io_status_assert):
            yield result
        io_sche=self.host_status['io_sche'][-1]['scheduler']
        if io_sche!='deadline':
            yield {
                'host_status':"io_sche",
                "message":'机器设备{0}({1})调度算法不是 deadline'.format(data_device,io_sche)
            }
        



    def table_advistor(self):
        # 自增 id 检查
        # 业务表都是 innodb
        # 主键或者唯一索引检查
        for schema,tables in self.tables.items():
            if schema in ('mysql','inforamtion_schema','performance_schema','sys'):
                continue
            for table,v in tables.items():
                if v['ENGINE']!='InnoDB':
                    yield {
                        "table_status":'engine_check',
                        "message":"{0}.{1} table is not a InnoDB table".format(schema,table)
                    }
                unq_indexs={}
                for index,values in v['index'].itmes():
                    if  values['NON_UNIQUE']==0:
                        unq_indexs[index]=table['index'][index]
                if len(unq_indexs)==0:
                    yield {
                        "table_status":"primary_key_check",
                        "message":"{0}.{1} table no primary key or unique key".format(schema,table)
                    }
                if v['AUTO_INCREMENT'] is not None:
                    inc_value=v['AUTO_INCREMENT']
                    #如果存在自增 id，则该列必定为主键 并且有只有自增列为主键
                    auto_col=unq_indexs['PRIMARY']['columns'][0]
                    inc_type=v['columns'][auto_col]['DATA_TYPE']
                    # 参考范围
                    # tinyint 127，unsigned 255
                    # smaillint 32767 ，unsigned 65535
                    # mediumint 8366607，unsigned  16777215
                    # int 2147483647 unsigned 4294967295
                    # bigint 9223372036854775807 unsigned 9223372036854775807
                    int_range={
                        "tinyint":{
                            'normal':127,
                            'unsigned':255
                        },
                        "smaillint":{
                            'normal':32767,
                            'unsigned':65535
                        },
                        "mediumint":{
                            'normal':8366607,
                            'unsigned':16777215
                        },
                        "int":{
                            'normal':2147483647,
                            'unsigned':4294967295
                        },
                        "bigint":{
                            'normal':9223372036854775807,
                            'unsigned':9223372036854775807
                        },
                    }
                    if 'int' not in inc_type:
                        yield {
                            "table_check":"increment_type",
                            "message":"{0}.{1} 表自增 ID 不是 int 类型".format(schema,table)
                        }
                    auto_inc_result=False
                    # int 类型在最后处理
                    for name in ['tinyint','smaillint','mediumint','bigint','int']:
                        if name in inc_type:
                            if 'unsigned' in inc_type:
                                # 如果到达90%的使用量，则认为存在问题
                                if inc_value>(int_range[name]['unsigned']*0.9):
                                    yield {
                                        "table_check":"increment_value",
                                        'message':"{0}.{1} 表自增ID ({2}/{3}) 将要用满，请检查".format(schema,table,inc_value,int_range[name]['unsigned'])
                                    }
                            else:
                                if inc_value>(int_range[name]['normal']*0.9):
                                    yield {
                                        "table_check":"increment_value",
                                        'message':"{0}.{1} 表自增ID ({2}/{3}) 将要用满，请检查".format(schema,table,inc_value,int_range[name]['unsigned'])
                                    }
                            break
        return None


    
    def report(self):

        '''
        本部分主要检测单个实例的状况
        MySQL 的检查主要分为以下一些部分：
        1. 操作系统
            CPU
            内存
            磁盘容量
            磁盘 iops
        2. MySQL
            变量检查
            状态检查
        3. 表结构检查
        4. 资源检查
        '''
        define={
            "resource":{
                "cpus":0,
                "mems":0,
                "storage_type":"SSD",
                "storage_size":0
            },
            'masterslave':{
                "is_master":True,
            },
            'instance':{
                'mounted_dir':"/data",
                'data_device':'vdb',
                'user':'mysql'
            },
            'mysql':{
                'host':'',
                "port":3306,
                'username':'',
                'password':"",
                'schema':""
            }
        }
        self.is_master=self.metrics['masterslave']['is_master']
        self.variables=self.metrics['variables']
        self.tables=self.metrics['tables']
        self.errorlog=self.metrics['log']['error_log']
        self.status=self.metrics['status']
        self.instance_status=self.metrics['instance_status']
        self.host_status=self.metrics['host_status']
        self.summary=self.metrics['summary']


class ReportCollect(self):

    def __init__(self):

        #必须的参数
        # mysql 连接信息
        # mysql 数据目录
        # mysql 数据设备
        pass