from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

import env


def init_tracing():
    # 1. Định nghĩa Resource (Tên service)
    resource = Resource.create({SERVICE_NAME: env.SERVICE_NAME})

    # 2. Cấu hình OTLP Exporter gửi đến Honeycomb
    # Lưu ý: Python SDK thường dùng /v1/traces nếu dùng HTTP
    exporter = OTLPSpanExporter(
        endpoint="https://api.honeycomb.io/v1/traces",
        headers={"x-honeycomb-team": env.HONEYCOMB_API_KEY},
    )

    # 3. Thiết lập Provider và Processor
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # Đăng ký provider toàn cục
    trace.set_tracer_provider(provider)
    logger.success(f"Tracing initialized for {env.SERVICE_NAME}")
