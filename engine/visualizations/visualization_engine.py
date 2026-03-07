"""Professional visualization engine for consulting-grade reports.

Uses matplotlib, seaborn, and plotly to generate high-quality charts
including risk distribution donuts, risk matrices, financial exposure
bar charts, and radar charts.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle, Circle
from matplotlib.colors import LinearSegmentedColormap


# Set professional style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10


class VisualizationEngine:
    """Generate professional charts for risk assessment reports."""
    
    def __init__(self, color_scheme: str = "corporate"):
        """Initialize visualization engine.
        
        Args:
            color_scheme: Color palette name ("corporate", "risk", "consulting")
        """
        self.color_schemes = {
            "corporate": {
                "primary": "#4C3D75",
                "secondary": "#6B5B95",
                "accent": "#88B04B",
                "critical": "#E74C3C",
                "high": "#E67E22",
                "moderate": "#F39C12",
                "low": "#27AE60",
                "minimal": "#3498DB",
                "background": "#FFFFFF",
                "text": "#2C3E50"
            },
            "risk": {
                "critical": "#C0392B",
                "high": "#E67E22",
                "moderate": "#F1C40F",
                "low": "#27AE60",
                "minimal": "#3498DB",
                "primary": "#34495E",
                "secondary": "#7F8C8D"
            }
        }
        self.colors = self.color_schemes.get(color_scheme, self.color_schemes["corporate"])
    
    def generate_risk_distribution_donut(
        self,
        data: Dict[str, int],
        title: str = "Risk Distribution",
        width: int = 800,
        height: int = 600
    ) -> str:
        """Generate a professional donut chart for risk distribution.
        
        Args:
            data: Dictionary mapping risk levels to counts (e.g., {"Critical": 5, "High": 3})
            title: Chart title
            width: Output width in pixels
            height: Output height in pixels
            
        Returns:
            Base64-encoded SVG string
        """
        # Map risk levels to colors
        risk_colors = {
            "Critical": self.colors.get("critical", "#E74C3C"),
            "High": self.colors.get("high", "#E67E22"),
            "Moderate": self.colors.get("moderate", "#F39C12"),
            "Low": self.colors.get("low", "#27AE60"),
            "Minimal": self.colors.get("minimal", "#3498DB")
        }
        
        labels = list(data.keys())
        values = list(data.values())
        colors = [risk_colors.get(label, "#95A5A6") for label in labels]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Create donut chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.0f%%',
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
            textprops={'fontsize': 11, 'weight': 'bold'}
        )
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        # Add center circle for donut effect
        centre_circle = Circle((0, 0), 0.20, fc='white', linewidth=0)
        ax.add_artist(centre_circle)
        
        # Add title
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        
        # Add total count in center
        total = sum(values)
        ax.text(0, 0, f"{total}\nTotal", ha='center', va='center', 
                fontsize=12, weight='bold', color=self.colors.get("text", "#2C3E50"))
        
        # Equal aspect ratio ensures pie is drawn as a circle
        ax.axis('equal')
        
        # Add legend
        ax.legend(wedges, [f"{label} ({value})" for label, value in zip(labels, values)],
                 title="Risk Levels",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1),
                 fontsize=9)
        
        plt.tight_layout()
        
        # Convert to SVG
        svg_buffer = io.StringIO()
        fig.savefig(svg_buffer, format='svg', bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        svg_buffer.seek(0)
        svg_data = svg_buffer.getvalue()
        plt.close(fig)
        
        # Encode as base64
        return base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')
    
    def generate_risk_matrix_heatmap(
        self,
        items: List[Dict[str, Any]],
        title: str = "Risk Matrix",
        width: int = 800,
        height: int = 600
    ) -> str:
        """Generate a professional risk matrix heatmap.
        
        Args:
            items: List of risk items with likelihood, impact, and severity
            title: Chart title
            width: Output width in pixels
            height: Output height in pixels
            
        Returns:
            Base64-encoded SVG string
        """
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Create 5x5 grid
        grid = np.zeros((5, 5))
        
        # Color map for risk zones
        colors_list = [
            (0.0, "#27AE60"),   # Low - Green
            (0.25, "#F1C40F"),  # Moderate - Yellow
            (0.5, "#F39C12"),   # Medium-High - Orange
            (0.75, "#E67E22"),  # High - Dark Orange
            (1.0, "#C0392B")    # Critical - Red
        ]
        cmap = LinearSegmentedColormap.from_list("risk_matrix", colors_list)
        
        # Create background heatmap
        risk_values = np.array([
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [5, 6, 7, 8, 9]
        ])
        
        im = ax.imshow(risk_values, cmap=cmap, aspect='equal', alpha=0.3)
        
        # Add grid
        ax.set_xticks(np.arange(5))
        ax.set_yticks(np.arange(5))
        ax.set_xticklabels(['1', '2', '3', '4', '5'])
        ax.set_yticklabels(['5', '4', '3', '2', '1'])  # Reverse for impact
        
        # Labels
        ax.set_xlabel('Likelihood', fontsize=11, weight='bold')
        ax.set_ylabel('Impact', fontsize=11, weight='bold')
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        
        # Add zone labels
        zone_labels = [
            (0, 4, 'Low', '#27AE60'),
            (1, 3, 'Moderate', '#F1C40F'),
            (2, 2, 'High', '#F39C12'),
            (3, 1, 'Critical', '#E67E22'),
            (4, 0, 'Critical', '#C0392B')
        ]
        
        for x, y, label, color in zone_labels:
            ax.text(x, y, label, ha='center', va='center', 
                   fontsize=10, weight='bold', color=color, alpha=0.7)
        
        # Plot risk items
        for item in items:
            likelihood = item.get('likelihood', 3) - 1  # Convert to 0-indexed
            impact = 5 - item.get('impact', 3)  # Reverse and convert to 0-indexed
            label = item.get('id', 'R')
            severity = item.get('severity', 'Moderate')
            
            # Color based on severity
            if severity == 'Critical':
                marker_color = '#C0392B'
            elif severity == 'High':
                marker_color = '#E67E22'
            elif severity == 'Moderate':
                marker_color = '#F39C12'
            else:
                marker_color = '#27AE60'
            
            ax.plot(likelihood, impact, 'o', markersize=15, color=marker_color, 
                   markeredgecolor='white', markeredgewidth=2, zorder=5)
            ax.annotate(label, (likelihood, impact), textcoords="offset points", 
                       xytext=(0, -15), ha='center', fontsize=8, weight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Risk Score', fontsize=10, weight='bold')
        
        plt.tight_layout()
        
        # Convert to SVG
        svg_buffer = io.StringIO()
        fig.savefig(svg_buffer, format='svg', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        svg_buffer.seek(0)
        svg_data = svg_buffer.getvalue()
        plt.close(fig)
        
        return base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')
    
    def generate_financial_exposure_chart(
        self,
        scenarios: List[Dict[str, Any]],
        title: str = "Financial Exposure by Scenario",
        width: int = 800,
        height: int = 500
    ) -> str:
        """Generate a professional bar chart for financial exposure.
        
        Args:
            scenarios: List of scenario dictionaries with name, min, max values
            title: Chart title
            width: Output width in pixels
            height: Output height in pixels
            
        Returns:
            Base64-encoded SVG string
        """
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Extract data
        names = [s['name'] for s in scenarios]
        min_values = [s.get('min', 0) / 1_000_000 for s in scenarios]  # Convert to millions
        max_values = [s.get('max', 0) / 1_000_000 for s in scenarios]
        
        # Colors
        colors_list = ['#27AE60', '#F39C12', '#E67E22', '#C0392B']
        
        x = np.arange(len(names))
        width_bar = 0.6
        
        # Create bars
        bars = ax.bar(x, max_values, width_bar, label='Maximum', color=colors_list[:len(names)], 
                     alpha=0.8, edgecolor='white', linewidth=2)
        
        # Add value labels on bars
        for i, (bar, max_val) in enumerate(zip(bars, max_values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${max_val:.1f}M',
                   ha='center', va='bottom', fontsize=10, weight='bold')
        
        # Style the chart
        ax.set_ylabel('Exposure (Millions USD)', fontsize=11, weight='bold')
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(names, fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        
        # Convert to SVG
        svg_buffer = io.StringIO()
        fig.savefig(svg_buffer, format='svg', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        svg_buffer.seek(0)
        svg_data = svg_buffer.getvalue()
        plt.close(fig)
        
        return base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')
    
    def generate_radar_chart(
        self,
        dimensions: List[str],
        values: List[float],
        title: str = "Multi-Dimensional Risk Analysis",
        width: int = 700,
        height: int = 700
    ) -> str:
        """Generate a professional radar/spider chart.
        
        Args:
            dimensions: List of dimension labels
            values: List of values (1-5 scale)
            title: Chart title
            width: Output width in pixels
            height: Output height in pixels
            
        Returns:
            Base64-encoded SVG string
        """
        # Number of variables
        N = len(dimensions)
        
        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        values += values[:1]  # Complete the loop
        angles += angles[:1]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100, subplot_kw=dict(projection='polar'))
        
        # Draw the radar chart
        ax.plot(angles, values, 'o-', linewidth=2, color='#4C3D75', label='Risk Profile')
        ax.fill(angles, values, alpha=0.25, color='#4C3D75')
        
        # Add dimension labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=10)
        
        # Set y-axis limits and labels
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8, color='gray')
        
        # Add grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.5)
        ax.xaxis.grid(True, linestyle='--', alpha=0.5)
        
        # Add title
        ax.set_title(title, fontsize=14, weight='bold', pad=30)
        
        plt.tight_layout()
        
        # Convert to SVG
        svg_buffer = io.StringIO()
        fig.savefig(svg_buffer, format='svg', bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        svg_buffer.seek(0)
        svg_data = svg_buffer.getvalue()
        plt.close(fig)
        
        return base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')


# Convenience functions for direct use
def generate_risk_distribution_chart(data: Dict[str, int], **kwargs) -> str:
    """Generate risk distribution donut chart."""
    engine = VisualizationEngine()
    return engine.generate_risk_distribution_donut(data, **kwargs)


def generate_risk_matrix_chart(items: List[Dict], **kwargs) -> str:
    """Generate risk matrix heatmap."""
    engine = VisualizationEngine()
    return engine.generate_risk_matrix_heatmap(items, **kwargs)


def generate_financial_exposure_chart(scenarios: List[Dict], **kwargs) -> str:
    """Generate financial exposure bar chart."""
    engine = VisualizationEngine()
    return engine.generate_financial_exposure_chart(scenarios, **kwargs)


def generate_radar_chart(dimensions: List[str], values: List[float], **kwargs) -> str:
    """Generate multi-dimensional risk radar chart."""
    engine = VisualizationEngine()
    return engine.generate_radar_chart(dimensions, values, **kwargs)
