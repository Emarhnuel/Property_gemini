"""
Interior Design Crew - Sequential process for room redesign visualization.

This crew handles the Design Phase:
1. Design Coordinator - Analyzes property images to identify room types
2. Room Redesigner - Uses Gemini tools to generate redesigned images
3. Report Agent - Compiles before/after images into JSON report

Process: Sequential - Each step depends on the previous output.
"""

from typing import List, Tuple, Any
import os
import json

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput

from real_ai_agents.tools.gemini_image_tools import (
    redesign_room_image,
    generate_room_description,
    suggest_design_styles,
)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ============== GUARDRAILS ==============

def validate_room_analysis(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate that room analysis contains required fields."""
    try:
        if isinstance(result.raw, str):
            try:
                data = json.loads(result.raw.replace("```json", "").replace("```", "").strip())
            except json.JSONDecodeError:
                return (False, "Output must be valid JSON")
        else:
            data = result.raw
        
        errors = []
        
        if "properties" not in data:
            errors.append("Missing 'properties' array")
        elif not isinstance(data["properties"], list):
            errors.append("'properties' must be an array")
        else:
            for i, prop in enumerate(data["properties"]):
                if "property_id" not in prop:
                    errors.append(f"Property {i+1} missing property_id")
                if "rooms" not in prop or not isinstance(prop.get("rooms"), list):
                    errors.append(f"Property {i+1} missing 'rooms' array")
        
        if errors:
            return (False, "Validation failed:\n" + "\n".join(errors))
        
        return (True, result.raw)
        
    except Exception as e:
        return (False, f"Validation error: {str(e)}")


def validate_design_report(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate the final design report has all required sections."""
    try:
        if isinstance(result.raw, str):
            try:
                data = json.loads(result.raw.replace("```json", "").replace("```", "").strip())
            except json.JSONDecodeError:
                return (False, "Output must be valid JSON")
        else:
            data = result.raw
        
        errors = []
        
        if "metadata" not in data:
            errors.append("Missing metadata section")
        
        if "properties" not in data or not isinstance(data.get("properties"), list):
            errors.append("Missing or invalid properties array")
        
        if errors:
            return (False, "Report validation failed:\n" + "\n".join(errors))
        
        return (True, result.raw)
        
    except Exception as e:
        return (False, f"Validation error: {str(e)}")


nova_llm = LLM(
    model="bedrock/us.amazon.nova-2-lite-v1:0",
    temperature=0.1,
)


nova_llm2 = LLM(
    model="bedrock/us.amazon.nova-2-pro-v1:0",
    temperature=0.1,
)


@CrewBase
class InteriorDesignCrew:
    """Interior Design Crew - Sequential process for room visualization.
    
    This crew handles the Design Phase:
    - Analyze room images from research results
    - Generate AI-powered room redesigns using Gemini
    - Compile before/after comparisons into JSON report
    
    Process: Sequential - Analysis -> Redesign -> Report compilation.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def design_coordinator(self) -> Agent:
        """Design coordinator that analyzes room images."""
        return Agent(
            config=self.agents_config["design_coordinator"],  # type: ignore[index]
            verbose=True,
            llm=nova_llm,
            max_iter=6,
            cache=True,
            tools=[generate_room_description],
        )
 
    @agent
    def room_redesigner(self) -> Agent:
        """Room redesigner that generates transformed room images."""
        return Agent(
            config=self.agents_config["room_redesigner"],  # type: ignore[index]
            verbose=True,
            llm=nova_llm,
            max_iter=10,
            max_rpm=10,
            cache=True,
            max_retry_limit=3,
            tools=[redesign_room_image, suggest_design_styles],
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent that compiles design results to JSON."""
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            verbose=True,
            llm=nova_llm,
            max_iter=5,
            cache=True,
        )

    @task
    def analyze_room_images(self) -> Task:
        """Task to analyze room images from research results."""
        return Task(
            config=self.tasks_config["analyze_room_images"],  # type: ignore[index]
            guardrail=validate_room_analysis,
            guardrail_max_retries=2,
        )

    @task
    def generate_redesigns(self) -> Task:
        """Task to generate redesigned room visualizations."""
        return Task(
            config=self.tasks_config["generate_redesigns"],  # type: ignore[index]
        )

    @task
    def compile_design_report(self) -> Task:
        """Task to compile all designs into JSON report."""
        return Task(
            config=self.tasks_config["compile_design_report"],  # type: ignore[index]
            output_file="output/design_results.json",
            guardrail=validate_design_report,
            guardrail_max_retries=2,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Interior Design Crew with sequential process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=False,
            verbose=True,
        )
