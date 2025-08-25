import multiprocessing

bind = '0.0.0.0:8000'

workers = multiprocessing.cpu_count() * 2 + 1

max_requests = 2000
max_requests_jitter = 400

accesslog = '-'
chdir = '/code'
worker_tmp_dir = '/dev/shm'  # noqa: S108
