from enum import Enum


class SupportedAttachmentVisualizationMimeTypes(Enum):
    """The MIME types supported for viewing files in the application."""

    IMAGE_WEBP = 'image/webp'
    IMAGE_PNG = 'image/png'
    IMAGE_JPEG = 'image/jpeg'
    IMAGE_JPG = 'image/jpg'
    IMAGE_GIF = 'image/gif'
    IMAGE_BMP = ('image/bmp',)
    IMAGE_AVIF = 'image/avif'
    IMAGE_TIFF = 'image/tiff'
    APPLICATION_JSON = 'application/json'
    APPLICATION_XML = 'application/xml'
    TEXT_CSV = 'text/csv'
    TEXT_PLAIN = 'text/plain'
    TEXT_MARKDOWN = 'text/markdown'


def can_view_attachment(mime_type: str) -> bool:
    """Determines if a MIME type can be displayed by the application directly in the terminal.

    Args:
        mime_type: the MIME type. For detail see https://www.iana.org/assignments/media-types/media-types.xhtml

    Returns:
        `True` if the application supports visualizing content of the given MIME type; `False` otherwise.
    """
    try:
        SupportedAttachmentVisualizationMimeTypes(mime_type)
        return True
    except ValueError:
        return False


def is_image(mime_type: str) -> bool:
    """Determines if a MIME type refers to an image type supported by the application.

    Args:
        mime_type: the MIME type. For detail see https://www.iana.org/assignments/media-types/media-types.xhtml

    Returns:
        `True` if the MIME type represents an image file supported by the application; `False` otherwise.
    """
    return mime_type in [
        SupportedAttachmentVisualizationMimeTypes.IMAGE_WEBP.value,
        SupportedAttachmentVisualizationMimeTypes.IMAGE_PNG.value,
        SupportedAttachmentVisualizationMimeTypes.IMAGE_JPG.value,
        SupportedAttachmentVisualizationMimeTypes.IMAGE_JPEG.value,
        SupportedAttachmentVisualizationMimeTypes.IMAGE_BMP.value,
        SupportedAttachmentVisualizationMimeTypes.IMAGE_GIF.value,
        SupportedAttachmentVisualizationMimeTypes.IMAGE_AVIF.value,
        SupportedAttachmentVisualizationMimeTypes.IMAGE_TIFF.value,
    ]
