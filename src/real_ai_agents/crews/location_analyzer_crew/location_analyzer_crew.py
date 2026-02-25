from typing import List, Tuple, Any
import os
import json

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput

from real_ai_agents.tools.google_maps_tools import google_places_geocode_tool, google_places_nearby_tool


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ============== GUARDRAILS ==============

def validate_location_analysis(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate that location analysis contains all 8 amenity categories and required fields."""
    try:
        # Parse the result
        if isinstance(result.raw, str):
            try:
                data = json.loads(result.raw)
            except json.JSONDecodeError:
                return (False, "Output must be valid JSON")
        else:
            data = result.raw
        
        required_amenities = [
            "markets", "gyms", "bus_parks", "railway_terminals",
            "stadiums", "malls", "airports", "seaports"
        ]
        
        errors = []
        
        # Check property_id
        if not data.get("property_id"):
            errors.append("Missing property_id")
        
        # Check coordinates
        coords = data.get("coordinates", {})
        if not coords.get("lat") or not coords.get("lng"):
            errors.append("Missing coordinates (lat/lng)")
        
        # Check all amenity categories exist
        amenities = data.get("amenities", {})
        for amenity in required_amenities:
            if amenity not in amenities:
                errors.append(f"Missing amenity category: {amenity}")
            else:
                # Each amenity should have a score
                if "score" not in amenities[amenity]:
                    errors.append(f"Missing score for {amenity}")
        
        # Check overall_score
        if "overall_score" not in data:
            errors.append("Missing overall_score")
        
        # Check advantages and disadvantages
        if "advantages" not in data or not isinstance(data.get("advantages"), list):
            errors.append("Missing or invalid advantages array")
        if "disadvantages" not in data or not isinstance(data.get("disadvantages"), list):
            errors.append("Missing or invalid disadvantages array")
        
        if errors:
            return (False, "Validation failed:\n" + "\n".join(errors))
        
        return (True, result.raw)
        
    except Exception as e:
        return (False, f"Validation error: {str(e)}")


def validate_location_report(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate the final location report has all required sections."""
    try:
        if isinstance(result.raw, str):
            try:
                data = json.loads(result.raw)
            except json.JSONDecodeError:
                return (False, "Output must be valid JSON")
        else:
            data = result.raw
        
        errors = []
        
        # Check metadata
        if "metadata" not in data:
            errors.append("Missing metadata section")
        
        # Check properties array
        if "properties" not in data or not isinstance(data.get("properties"), list):
            errors.append("Missing or invalid properties array")
        elif len(data["properties"]) == 0:
            errors.append("Properties array is empty")
        
        # Check comparison section (if multiple properties)
        if len(data.get("properties", [])) > 1 and "comparison" not in data:
            errors.append("Missing comparison section for multiple properties")
        
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
class LocationAnalyzerCrew:
    """Location Analyzer Crew - Hierarchical process for geospatial analysis.
    
    This crew handles the Intelligence Phase:
    - Manager assigns approved properties (max 6) to analyzer agents
    - Each analyzer handles ALL 8 amenity types for one property
    - Analyzers work in parallel using async_execution
    - Report agent compiles results to JSON
    
    Process: Hierarchical - Manager coordinates parallel property analysis.
    
    Amenity Types (6km radius, 50km for airports):
    - Markets, Gyms, Bus parks, Railway terminals
    - Stadiums, Malls, Airports, Seaports
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def manager(self) -> Agent:
        """Manager agent that coordinates property assignments."""
        return Agent(
            config=self.agents_config["manager"],  # type: ignore[index]
            verbose=True,
            llm=nova_llm2,
            max_iter=8,
            cache=True,
        )

    @agent
    def location_analyzer_1(self) -> Agent:
        """Location analyzer for property 1."""
        return Agent(
            config=self.agents_config["location_analyzer"],  # type: ignore[index]
            respect_context_window=True,
            verbose=True,
            llm=nova_llm,
            max_iter=6,
            max_rpm=15,
            cache=True,
            max_retry_limit=3,
            tools=[google_places_geocode_tool, google_places_nearby_tool],
        )

    @agent
    def location_analyzer_2(self) -> Agent:
        """Location analyzer for property 2."""
        return Agent(
            config=self.agents_config["location_analyzer"],  # type: ignore[index]
            respect_context_window=True,
            verbose=True,
            llm=nova_llm,
            max_iter=6,
            max_rpm=15,
            cache=True,
            max_retry_limit=3,
            tools=[google_places_geocode_tool, google_places_nearby_tool],
        )

    @agent
    def location_analyzer_3(self) -> Agent:
        """Location analyzer for property 3."""
        return Agent(
            config=self.agents_config["location_analyzer"],  # type: ignore[index]
            respect_context_window=True,
            verbose=True,
            llm=nova_llm,
            max_iter=6,
            max_rpm=15,
            cache=True,
            max_retry_limit=3,
            tools=[google_places_geocode_tool, google_places_nearby_tool],
        )

    @agent
    def location_analyzer_4(self) -> Agent:
        """Location analyzer for property 4."""
        return Agent(
            config=self.agents_config["location_analyzer"],  # type: ignore[index]
            respect_context_window=True,
            verbose=True,
            llm=nova_llm,
            max_iter=6,
            max_rpm=15,
            cache=True,
            max_retry_limit=3,
            tools=[google_places_geocode_tool, google_places_nearby_tool],
        )

    @agent
    def location_analyzer_5(self) -> Agent:
        """Location analyzer for property 5."""
        return Agent(
            config=self.agents_config["location_analyzer"],  # type: ignore[index]
            respect_context_window=True,
            verbose=True,
            llm=nova_llm,
            max_iter=6,
            max_rpm=15,
            cache=True,
            max_retry_limit=3,
            tools=[google_places_geocode_tool, google_places_nearby_tool],
        )

    @agent
    def location_analyzer_6(self) -> Agent:
        """Location analyzer for property 6."""
        return Agent(
            config=self.agents_config["location_analyzer"],  # type: ignore[index]
            respect_context_window=True,
            verbose=True,
            llm=nova_llm,
            max_iter=6,
            max_rpm=15,
            cache=True,
            max_retry_limit=3,
            tools=[google_places_geocode_tool, google_places_nearby_tool],
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent that compiles location intelligence to JSON."""
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            verbose=True,
            llm=nova_llm2,
            max_iter=5,
            cache=True,
        )

    @task
    def assign_properties(self) -> Task:
        """Task for manager to assign properties to analyzers."""
        return Task(
            config=self.tasks_config["assign_properties"],  # type: ignore[index]
        )

    @task
    def analyze_property_1(self) -> Task:
        """Async task for analyzer 1."""
        return Task(
            config=self.tasks_config["analyze_property"],  # type: ignore[index]
            agent=self.location_analyzer_1(),
            async_execution=True,
            guardrail=validate_location_analysis,
            guardrail_max_retries=2,
        )

    @task
    def analyze_property_2(self) -> Task:
        """Async task for analyzer 2."""
        return Task(
            config=self.tasks_config["analyze_property"],  # type: ignore[index]
            agent=self.location_analyzer_2(),
            async_execution=True,
            guardrail=validate_location_analysis,
            guardrail_max_retries=2,
        )

    @task
    def analyze_property_3(self) -> Task:
        """Async task for analyzer 3."""
        return Task(
            config=self.tasks_config["analyze_property"],  # type: ignore[index]
            agent=self.location_analyzer_3(),
            async_execution=True,
            guardrail=validate_location_analysis,
            guardrail_max_retries=2,
        )

    @task
    def analyze_property_4(self) -> Task:
        """Async task for analyzer 4."""
        return Task(
            config=self.tasks_config["analyze_property"],  # type: ignore[index]
            agent=self.location_analyzer_4(),
            async_execution=True,
            guardrail=validate_location_analysis,
            guardrail_max_retries=2,
        )

    @task
    def analyze_property_5(self) -> Task:
        """Async task for analyzer 5."""
        return Task(
            config=self.tasks_config["analyze_property"],  # type: ignore[index]
            agent=self.location_analyzer_5(),
            async_execution=True,
            guardrail=validate_location_analysis,
            guardrail_max_retries=2,
        )

    @task
    def analyze_property_6(self) -> Task:
        """Async task for analyzer 6."""
        return Task(
            config=self.tasks_config["analyze_property"],  # type: ignore[index]
            agent=self.location_analyzer_6(),
            async_execution=True,
            guardrail=validate_location_analysis,
            guardrail_max_retries=2,
        )

    @task
    def compile_location_report(self) -> Task:
        """Task to compile all location analysis into JSON report."""
        return Task(
            config=self.tasks_config["compile_location_report"],  # type: ignore[index]
            output_file="output/location_intelligence.json",
            guardrail=validate_location_report,
            guardrail_max_retries=2,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Location Analyzer Crew with hierarchical process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.manager(),
            memory=False,
            planning=True,
            verbose=True,
            
        )

