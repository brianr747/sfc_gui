from sfc_models import register_standard_logs
import sfc_models.gl_book.chapter6 as chapter6


def get_description():
    return 'Model REG'


def build_model():
    builder = chapter6.REG2('CA')
    return builder.build_model()