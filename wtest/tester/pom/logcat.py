import os
import asyncio
import time

from base import log

LOGCAT_LEVEL_STR = [' V ', ' D ', ' I ', ' W ', ' E ', ' F ', ' S ']


class LogBean:
    __TAG = 'LogBean'

    @staticmethod
    def get(content: str):
        log.d(LogBean.__TAG,
              'get -------------------------------------------------------------------------------------->')

        if content is None:
            log.w(LogBean.__TAG, 'content is None')
            log.d(LogBean.__TAG,
                  'get failed -------------------------------------------------------------------------------------->')
            return None

        if not isinstance(content, str):
            content = str(content)

        # 03-21 10:00:00.123 12345 6789 I ActivityManager: Starting: Intent { cmp=com.example.myapp/.MainActivity }
        log.d(LogBean.__TAG, 'content = %s' % content)

        level = None
        level_len = 0
        split_idx = None
        for lls in LOGCAT_LEVEL_STR:
            try:
                split_idx = content.index(lls)
                level_len = len(lls)
                level = lls.strip()
            except ValueError:
                pass

        if (split_idx is None
                or split_idx + level_len >= len(content)
                or split_idx <= 0):
            log.w(LogBean.__TAG, 'split_idx = %s' % str(split_idx))
            log.d(LogBean.__TAG,
                  'get failed -------------------------------------------------------------------------------------->')
            return None

        pre = content[:split_idx].strip()
        # 03-21 10:00:00.123 12345 6789
        pre_items = pre.split(' ')
        pre_items = list(filter(lambda x: len(x.strip()) != 0, pre_items))
        if len(pre_items) != 4:
            log.w(LogBean.__TAG, 'pre_items length = %s ' % str(len(pre_items)))
            log.d(LogBean.__TAG,
                  'get failed -------------------------------------------------------------------------------------->')
            return None

        # ActivityManager: Starting: Intent { cmp=com.example.myapp/.MainActivity }
        after = content[split_idx + level_len:]
        after_split_idx = None
        try:
            after_split_idx = after.index(':')
        except ValueError:
            pass
        if (after_split_idx is None
                or after_split_idx <= 0
                or after_split_idx + 1 >= len(after)):
            log.w(LogBean.__TAG, 'after_split_idx = %s' % str(after_split_idx))
            log.d(LogBean.__TAG,
                  'get failed -------------------------------------------------------------------------------------->')
            return None
        tag = after[:after_split_idx].strip()
        msg = after[after_split_idx + 1:].strip()

        if len(msg) == 0:
            log.w(LogBean.__TAG, 'msg is empty')
            log.d(LogBean.__TAG,
                  'get failed -------------------------------------------------------------------------------------->')
            return None

        log.d(LogBean.__TAG,
              'get success -------------------------------------------------------------------------------------->')

        return LogBean(pre_items[0], pre_items[1], pre_items[2], pre_items[3],
                       level, tag, msg)

    def __init__(self, date, time_str, pid, tid,
                 level, tag, msg):
        self.date = date
        self.time_str = time_str
        self.pid = pid
        self.tid = tid
        self.level = level
        self.tag = tag
        self.msg = msg

    def is_main(self):
        return self.pid == self.tid

    def assert_msg(self, func):
        if func and callable(func):
            log.d(LogBean.__TAG, 'msg = ' + self.msg)
            return func(self.msg)
        else:
            return False

    def __str__(self) -> str:
        return ('{ date=%s, time_str=%s, pid=%s, tid=%s, level=%s, tag=%s, msg=%s }' %
                (self.date, self.time_str, self.pid, self.tid, self.level, self.tag, self.msg))


class Logcat:
    __TAG = 'Logcat'

    def __init__(self, cmd: str):
        self.cmd = cmd
        self.out_text = ''
        self.err_text = ''
        self.log_bean_list = []

    async def exec(self):
        log.d(Logcat.__TAG, 'logcat start, cmd = %s' % self.cmd)
        process = await asyncio.create_subprocess_shell(
            self.cmd,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE
        )

        time.sleep(10)
        stdout, stderr = await process.communicate()

        self.out_text = stdout.decode(encoding='utf-8')
        self.err_text = stdout.decode(encoding='utf-8')

        for text in self.out_text.split(os.linesep):
            bean = LogBean.get(text)
            if bean is None:
                log.w(Logcat.__TAG, 'get LogBean failed; text = %s' % text)
                continue
            self.log_bean_list.append(bean)

        log.d(Logcat.__TAG, 'logcat start end')
