# gallery/templatetags/video_tags.py
from django import template
import re
import json

register = template.Library()

@register.filter
def youtube_id(url):
    """YouTube URL'sinden video ID'sini çıkarır"""
    if not url:
        return ''
    
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([^&\n?#]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ''

@register.filter
def vimeo_id(url):
    """Vimeo URL'sinden video ID'sini çıkarır"""
    if not url:
        return ''
    
    pattern = r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return ''

@register.simple_tag
def video_data_json(gallery_item):
    """Gallery item için video data JSON'ı oluşturur"""
    if gallery_item.media_type != 'video':
        return ''
    
    data = {'type': 'unknown'}
    
    if gallery_item.video:
        data = {
            'type': 'file',
            'src': gallery_item.video.url
        }
    elif gallery_item.video_url:
        if 'youtube' in gallery_item.video_url.lower():
            data = {
                'type': 'youtube',
                'id': youtube_id(gallery_item.video_url)
            }
        elif 'vimeo' in gallery_item.video_url.lower():
            data = {
                'type': 'vimeo', 
                'id': vimeo_id(gallery_item.video_url)
            }
    
    return json.dumps(data)