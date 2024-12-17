"""
This servicer module runs the LLM chain.

The chain is constructed to perform OCR first, run the
analyzer the second to fix problems found on OCR, and
translate the products into the given language.
"""
from backend.ai.assistants import AnalyzerAssistant
from backend.ai.assistants import OcrAssistant
from backend.ai.datatypes import OcrResponse
from backend.ai.datatypes import OcrStatus
from datatypes import OcrStatusTypes
from datatypes import Receipt


class PipelineError(BaseException):
    """This class represents errors in the pipeline."""


def run_pipeline(image_path: str) -> Receipt:
    """Run the assistants in a spesific order.

    :param image_path: The path to the receipt image.
    :raise PipelineError: AI assistants cannot process information.
    :return: The receipt instance.
    """
    ocr_agent: OcrAssistant = OcrAssistant()
    analyzer_agent: AnalyzerAssistant = AnalyzerAssistant()

    ocr_result: OcrResponse = ocr_agent.ask({"image": image_path})
    if ocr_result.ocr_status != OcrStatus.SUCCESS:
        error_msg: str = "The OCR assistant has failed. Please re-run."
        raise PipelineError(error_msg)

    corrected_ocr: OcrResponse = analyzer_agent.ask({"ocr_result": ocr_result})
    if corrected_ocr.ocr_status != OcrStatus.SUCCESS:
        error_msg: str = "The Analyzer assistant has failed. Please re-run."
        raise PipelineError(error_msg)

    return Receipt(
        receipt_id="receipt-12341234-1234-1234-12341234",
        ocr_status=OcrStatusTypes.SUCCESS if corrected_ocr.ocr_status == OcrStatus.SUCCESS else OcrStatusTypes.ERROR,
        store_name=corrected_ocr.store_name,
        store_address=corrected_ocr.store_address,
        date_time=corrected_ocr.date_time,
        category=[product.category for product in corrected_ocr.products],
        products=corrected_ocr.products,
    )
