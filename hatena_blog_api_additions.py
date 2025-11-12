# Add these methods to HatenaBlogAPI class

def get_entries(self, page: str = None) -> Dict[str, Any]:
    """
    Get list of blog entries
    
    Args:
        page: Page URL for pagination (optional)
        
    Returns:
        Dict with entries list and next page URL
    """
    try:
        headers = {
            'X-WSSE': self._create_wsse_header()
        }
        
        url = page if page else f"{self.endpoint}/entry"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'app': 'http://www.w3.org/2007/app'
            }
            
            entries = []
            for entry in root.findall('atom:entry', ns):
                title_elem = entry.find('atom:title', ns)
                link_elem = entry.find("atom:link[@rel='edit']", ns)
                draft_elem = entry.find('app:control/app:draft', ns)
                category_elems = entry.findall('atom:category', ns)
                
                entry_data = {
                    'title': title_elem.text if title_elem is not None else '',
                    'edit_url': link_elem.get('href') if link_elem is not None else '',
                    'is_draft': draft_elem.text == 'yes' if draft_elem is not None else False,
                    'categories': [cat.get('term') for cat in category_elems]
                }
                entries.append(entry_data)
            
            # Check for next page
            next_link = root.find("atom:link[@rel='next']", ns)
            next_page = next_link.get('href') if next_link is not None else None
            
            return {
                'success': True,
                'entries': entries,
                'next_page': next_page
            }
        else:
            logger.error(f"✗ Failed to get entries: {response.status_code}")
            return {
                'success': False,
                'error': response.text
            }
            
    except Exception as e:
        logger.error(f"✗ Error getting entries: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

def update_article_categories(self, edit_url: str, title: str, content: str, categories: list, draft: bool = True) -> Dict[str, Any]:
    """
    Update an existing article's categories (and other fields)
    
    Args:
        edit_url: Edit URL of the article
        title: Article title
        content: Article content
        categories: List of category names
        draft: Draft status
        
    Returns:
        Dict with success status
    """
    try:
        logger.info(f"Updating article categories: '{title}'")
        
        entry_xml = self._create_entry_xml(title, content, categories, draft)
        
        headers = {
            'X-WSSE': self._create_wsse_header(),
            'Content-Type': 'application/xml; charset=utf-8'
        }
        
        response = requests.put(edit_url, data=entry_xml.encode('utf-8'), headers=headers)
        
        if response.status_code == 200:
            logger.info("✓ Article updated successfully!")
            return {
                'success': True,
                'message': 'Article updated successfully'
            }
        else:
            logger.error(f"✗ Failed to update article: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {
                'success': False,
                'error': response.text
            }
            
    except Exception as e:
        logger.error(f"✗ Error updating article: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

def get_article_content(self, edit_url: str) -> Dict[str, Any]:
    """
    Get full content of an article by edit URL
    
    Args:
        edit_url: Edit URL of the article
        
    Returns:
        Dict with article data
    """
    try:
        headers = {
            'X-WSSE': self._create_wsse_header()
        }
        
        response = requests.get(edit_url, headers=headers)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'app': 'http://www.w3.org/2007/app'
            }
            
            title_elem = root.find('atom:title', ns)
            content_elem = root.find('atom:content', ns)
            draft_elem = root.find('app:control/app:draft', ns)
            
            return {
                'success': True,
                'title': title_elem.text if title_elem is not None else '',
                'content': content_elem.text if content_elem is not None else '',
                'is_draft': draft_elem.text == 'yes' if draft_elem is not None else False
            }
        else:
            logger.error(f"✗ Failed to get article: {response.status_code}")
            return {
                'success': False,
                'error': response.text
            }
            
    except Exception as e:
        logger.error(f"✗ Error getting article: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }
