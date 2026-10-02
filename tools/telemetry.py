import contextvars

current_user_id = contextvars.ContextVar("current_user_id", default="default_user")

def init_telemetry(service_name):
    pass

def get_tracer():
    class Tracer:
        def start_as_current_span(self, name):
            class Span:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
                def set_attribute(self, key, value):
                    pass
            return Span()
    return Tracer()
