from dataclasses import dataclass
import logging
import datetime
import functools
import multiprocessing
import os
from pathlib import Path
from pprint import pprint
import threading
import time
import traceback
import uuid

@dataclass
class ErrorsHandling:
    @staticmethod
    def create_log_file(correlation_id):
        logs_folder = Path('logs')
        date_folder = Path(datetime.datetime.now().strftime(r'%Y-%m-%d'))
        if correlation_id is None:
            correlation_id = 'no_correlation_id_' + str(uuid.uuid4())
        filename = logs_folder / date_folder / correlation_id
        if not os.path.exists(Path(filename).parent):
            os.makedirs(Path(filename).parent)
        logging.basicConfig(
            filename=filename, filemode='a+', level=logging.ERROR,
            format='%(asctime)s - %(levelname)s\n%(message)s')

    @staticmethod
    def resend_to_queue():
        def decorator_retry(func):
            @functools.wraps(func)
            def wrapper_retry(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    ErrorsHandling.create_log_file(args[2+1].correlation_id)
                    logging.error(traceback.format_exc())
                    traceback.print_exc()
                    args[0+1].basic_nack(delivery_tag=args[1+1].delivery_tag, requeue=True)
            return wrapper_retry
        return decorator_retry
    
    @staticmethod
    def queue_connection_loop():
        def decorator_retry(func):
            @functools.wraps(func)
            def wrapper_retry(*args, **kwargs):
                while True:
                    try:
                        func(*args, **kwargs)
                        threading.Event().wait()
                    except Exception:
                        # print(traceback.format_exc().strip().split('\n')[-1])
                        print(traceback.format_exc())
                        print(f'🔴 Restarting connection - {args[0].queue}')
                        time.sleep(10)
                        print(f'🟢 Starting connection - {args[0].queue}')
            return wrapper_retry
        return decorator_retry
