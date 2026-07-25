import contextvars
from opentelemetry import trace

current_user_id = contextvars.ContextVar("current_user_id", default="default_user")

def init_telemetry(service_name):
    pass

def get_tracer():
    return trace.get_tracer(__name__)
