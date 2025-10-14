from pathlib import Path

def load_html_template(template_name: str, **kwargs) -> str:
    """
    Загружает HTML шаблон и заменяет переменные.
    
    Args:
        template_name: Имя файла шаблона (например, 'email_body_code_confirmation.html')
        **kwargs: Переменные для замены в шаблоне
        
    Returns:
        str: HTML содержимое с замененными переменными
    """
    # Получаем путь к директории с шаблонами
    template_dir = Path(__file__).parent.parent.parent / "html_templates"
    template_path = template_dir / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found in {template_dir}")
    
    # Читаем содержимое шаблона
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Заменяем переменные в шаблоне
    for key, value in kwargs.items():
        placeholder = f"{{{{ {key} }}}}"
        content = content.replace(placeholder, str(value))
    
    return content
