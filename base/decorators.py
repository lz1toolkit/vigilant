import time
import traceback


class RetryException(Exception):

    def __init__(self, msg):
        self.msg = msg


def retry(retry_count=2, sleep_time=60, condition=None):
    def decorator(func):
        def inner_func(*args, **kwargs):
            count = 0
            last_exception = None
            while count < retry_count:
                try:
                    rt = func(*args, **kwargs)
                    last_exception = None
                    return rt
                except (RetryException, Exception) as exception:
                    traceback.print_exc()

                    last_exception = exception

                    is_retry = False
                    if isinstance(exception, RetryException):
                        is_retry = True
                    elif condition and callable(condition):
                        condition_rt = condition(exception)
                        if condition_rt and isinstance(condition_rt, bool):
                            is_retry = condition_rt

                    if is_retry:
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                        count = count + 1
                    else:
                        count = retry_count

            if last_exception:
                raise last_exception

        return inner_func

    return decorator


if __name__ == '__main__':
    st = 2


    @retry(3, st)
    def test_retry(content):
        print('test_retry: ' + content)
        raise RetryException()


    @retry(3, st)
    def test_retry_2(content):
        print('test_retry_2: ' + content)
        raise RuntimeError()


    class TestException(Exception):
        pass


    @retry(3, st, condition=lambda ex: isinstance(ex, TestException))
    def test_retry_3(content):
        print('test_retry_3: ' + content)
        raise TestException()


    @retry(3, st, condition=lambda ex: isinstance(ex, TestException))
    def test_retry_4(content):
        print('test_retry_4: ' + content)
        raise RecursionError()


    try:
        # 重试
        test_retry('hello 1')
    except Exception as e:
        traceback.print_exc()

    time.sleep(5)

    try:
        # 不重试
        test_retry_2('hello 2')
    except Exception as e:
        traceback.print_exc()

    time.sleep(5)

    try:
        # 重试
        test_retry_3('hello 3')
    except Exception as e:
        traceback.print_exc()

    time.sleep(5)

    try:
        # 不重试
        test_retry_4('hello 4')
    except Exception as e:
        traceback.print_exc()
