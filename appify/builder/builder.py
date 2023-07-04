from appify.builder.build_engine import BuildEngine
from appify.builder.objects import (
    BuildResult
)


def build(build_name, build_fingerprint, build_info: dict) -> BuildResult:
    ps = [build_name, build_fingerprint, build_info]
    for p in ps:
        if not p:
            return BuildResult(False,
                               'Invalid Param: build_name=%s, build_fingerprint=%s, build_info=%s' % (
                                   build_name, build_fingerprint, str(build_info)),
                               None)

    return BuildEngine(None).build(build_name, build_fingerprint, build_info)
