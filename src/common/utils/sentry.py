import sentry_sdk

from common.config import SentrySettings


def setup_sentry():
    config = SentrySettings()
    if config.enable and config.dsn:
        sentry_sdk.init(
            dsn=config.dsn,
            send_default_pii=config.send_pii,
            traces_sample_rate=config.traces_sample_rate,
            profiles_sample_rate=config.profiling_sample_rate
        )
        print("Sentry initialized")
