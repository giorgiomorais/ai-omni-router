"""
Chart Skills - Prepares Chart.js compatible payload structures for frontend rendering.
"""
from typing import Dict, Any, List
from app.skills.base import skill_registry

def generate_chart(
    chart_type: str,
    title: str,
    labels: List[str],
    values: List[float],
    dataset_label: str = "Total"
) -> Dict[str, Any]:
    """
    Gera a estrutura JSON compatível com Chart.js para renderização interativa na UI.
    Tipos suportados: 'bar', 'line', 'pie', 'doughnut'.
    """
    valid_types = ["bar", "line", "pie", "doughnut"]
    c_type = chart_type.lower() if chart_type.lower() in valid_types else "bar"
    
    # Cores modernas para dark mode
    palette = [
        "rgba(59, 130, 246, 0.8)",   # blue
        "rgba(16, 185, 129, 0.8)",   # emerald
        "rgba(245, 158, 11, 0.8)",   # amber
        "rgba(239, 68, 68, 0.8)",    # rose
        "rgba(139, 92, 246, 0.8)",   # purple
        "rgba(6, 182, 212, 0.8)",    # cyan
    ]
    
    background_colors = palette if c_type in ["pie", "doughnut"] else palette[0]
    border_colors = [c.replace("0.8", "1.0") for c in palette] if c_type in ["pie", "doughnut"] else palette[0].replace("0.8", "1.0")

    return {
        "status": "success",
        "chart_config": {
            "type": c_type,
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": dataset_label,
                    "data": values,
                    "backgroundColor": background_colors,
                    "borderColor": border_colors,
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": title,
                        "color": "#e2e8f0",
                        "font": {"size": 14, "weight": "bold"}
                    },
                    "legend": {
                        "labels": {"color": "#94a3b8"}
                    }
                },
                "scales": {} if c_type in ["pie", "doughnut"] else {
                    "x": {"ticks": {"color": "#94a3b8"}, "grid": {"color": "#334155"}},
                    "y": {"ticks": {"color": "#94a3b8"}, "grid": {"color": "#334155"}}
                }
            }
        }
    }

skill_registry.register(
    name="generate_chart",
    func=generate_chart,
    description="Gera a configuração gráfica pronta para renderizar no frontend via Chart.js (tipos: 'bar', 'line', 'pie', 'doughnut').",
    parameters={
        "type": "object",
        "properties": {
            "chart_type": {"type": "string", "enum": ["bar", "line", "pie", "doughnut"], "description": "Tipo do gráfico visual"},
            "title": {"type": "string", "description": "Título explicativo do gráfico"},
            "labels": {"type": "array", "items": {"type": "string"}, "description": "Rótulos do eixo X ou fatias da pizza"},
            "values": {"type": "array", "items": {"type": "number"}, "description": "Valores numéricos correspondentes"},
            "dataset_label": {"type": "string", "description": "Nome da série de dados", "default": "Total"}
        },
        "required": ["chart_type", "title", "labels", "values"]
    }
)
