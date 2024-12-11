from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

def render_prompt(template_name: str, context: dict) -> str:
    """
    Renders a single Jinja template with the provided context.

    Args:
        template_name (str): The name of the template file.
        context (dict): The context data to render the template.

    Returns:
        str: The rendered prompt.
    """
    template_dir = Path(__file__).parent / "prompts" / "jinja"
    env = Environment(
        loader=FileSystemLoader(searchpath=str(template_dir)),
        autoescape=select_autoescape(['j2'])
    )
    template = env.get_template(template_name)
    return template.render(context)
