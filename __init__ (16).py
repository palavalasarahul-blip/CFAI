"""Streamlit entry point for the Autonomous Cleaning Strategy Planner."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import AnalyticsTracker
from decision import Policy
from environment import CleaningTask, HouseEnvironment, Robot
from planner import HybridPlanner, PlanDecision
from search import SearchAlgorithm, compare_algorithms
from visualization import grid_figure, schedule_figure, search_figure

LOG_PATH = Path("cleaning_planner.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)

st.set_page_config(
    page_title="Autonomous Cleaning Strategy Planner",
    page_icon="AC",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #18212b; --muted: #66727f; --line: #dce3e8;
        --accent: #087e8b; --accent-soft: #e8f5f6; --surface: #ffffff;
    }
    .stApp { background: #f5f7f8; color: var(--ink); }
    .block-container { max-width: 1500px; padding-top: 1.5rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] {
        background: #ffffff; border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }
    [data-testid="stMetric"] {
        background: var(--surface); border: 1px solid var(--line); border-radius: 7px;
        padding: 12px 14px; min-height: 88px;
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--ink); }
    [data-testid="stForm"] {
        background: var(--surface); border: 1px solid var(--line);
        border-radius: 7px; padding: 1rem;
    }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label {
        color: var(--ink) !important;
        opacity: 1 !important;
    }
    [data-testid="stTabs"] button {
        color: #52606d !important;
        opacity: 1 !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--accent) !important;
    }
    [data-baseweb="select"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder {
        color: #8a96a1 !important;
        opacity: 1 !important;
    }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 7px; }
    [data-testid="stTabs"] button { padding-left: 1rem; padding-right: 1rem; }
    .status-strip {
        display: flex; flex-wrap: wrap; gap: 10px 22px; align-items: center;
        padding: 12px 15px; background: var(--surface);
        border: 1px solid var(--line); border-radius: 7px;
        margin: 0.75rem 0 1rem; color: var(--muted); font-size: 0.9rem;
    }
    .status-strip strong { color: var(--ink); }
    .explanation {
        background: var(--surface); border: 1px solid var(--line);
        border-left: 4px solid var(--accent); padding: 11px 14px;
        margin: 8px 0; border-radius: 0 6px 6px 0;
    }
    .section-note {
        color: var(--muted); font-size: 0.9rem; margin-top: -0.6rem;
        margin-bottom: 1rem;
    }
    .queue-empty {
        padding: 1.3rem; text-align: center; color: var(--muted);
        background: var(--surface); border: 1px dashed #bcc8cf; border-radius: 7px;
    }
    h1, h2, h3 { letter-spacing: 0 !important; }
    h1 { font-size: 2rem !important; }
    @media (max-width: 800px) {
        .block-container { padding: 1rem 0.75rem 2rem; }
        .status-strip { gap: 8px 14px; }
        h1 { font-size: 1.65rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_state() -> None:
    if "environment" not in st.session_state:
        environment = HouseEnvironment.demo()
        robot = Robot(position=(0, 0))
        environment.update_knowledge(robot)
        st.session_state.environment = environment
        st.session_state.robot = robot
        st.session_state.tracker = AnalyticsTracker(initial_dirt=len(environment.dirt))
        st.session_state.plan = None
        st.session_state.status = "Ready"
        st.session_state.running = False
        st.session_state.task_queue = []


def reset_state() -> None:
    for key in (
        "environment",
        "robot",
        "tracker",
        "plan",
        "status",
        "running",
        "task_queue",
    ):
        st.session_state.pop(key, None)
    initialize_state()


def generate_plan(
    algorithm: SearchAlgorithm, policy: Policy, auto_policy: bool
) -> PlanDecision:
    planner = HybridPlanner(st.session_state.environment, st.session_state.robot)
    active_tasks = [
        task
        for task in st.session_state.task_queue
        if task.status != "Completed"
    ]
    plan = planner.plan(
        algorithm,
        policy,
        auto_policy,
        requested_tasks=active_tasks or None,
    )
    st.session_state.plan = plan
    if active_tasks and plan.selected_room:
        for task in active_tasks:
            task.status = (
                "In Progress"
                if task.room_name == plan.selected_room
                else "Pending"
            )
    for assessment in plan.assessments:
        room = st.session_state.environment.rooms[assessment.room_name]
        actual = bool(room.cells & st.session_state.environment.dirt.keys())
        st.session_state.tracker.add_prediction(
            assessment.dirt_probability, actual
        )
    return plan


def execute_step(
    algorithm: SearchAlgorithm,
    policy: Policy,
    auto_policy: bool,
) -> None:
    plan: PlanDecision | None = st.session_state.plan
    if plan is None:
        return
    planner = HybridPlanner(st.session_state.environment, st.session_state.robot)
    action = planner.execute_next_step(plan)
    st.session_state.status = action
    st.session_state.tracker.record(
        action,
        st.session_state.robot.battery,
        st.session_state.robot.cleaned_cells,
        plan.selected_room,
    )
    target_finished = (
        st.session_state.robot.position == plan.target
        and st.session_state.robot.position not in st.session_state.environment.dirt
    )
    if target_finished:
        matching_task = next(
            (
                task
                for task in st.session_state.task_queue
                if task.room_name == plan.selected_room
                and task.status != "Completed"
            ),
            None,
        )
        if matching_task:
            matching_task.status = "Completed"
            remaining = [
                task
                for task in st.session_state.task_queue
                if task.status != "Completed"
            ]
            if remaining:
                completed_room = plan.selected_room
                next_plan = generate_plan(algorithm, policy, auto_policy)
                st.session_state.status = (
                    f"{completed_room} task completed. "
                    f"Next task: {next_plan.selected_room}."
                )
            else:
                st.session_state.plan = None
                st.session_state.running = False
                st.session_state.status = "All queued cleaning tasks are complete."
        else:
            st.session_state.running = False
    st.session_state.environment.update_knowledge(st.session_state.robot)


def ensure_task_dirt(room_name: str, intensity: float) -> None:
    environment = st.session_state.environment
    if environment.room_dirt(room_name):
        return
    room = environment.rooms[room_name]
    candidates = sorted(
        room.cells - environment.obstacles - environment.chargers
    )
    if candidates:
        environment.add_dirt(candidates[len(candidates) // 2], intensity)


def run_task_queue(
    algorithm: SearchAlgorithm,
    policy: Policy,
    auto_policy: bool,
) -> None:
    st.session_state.running = True
    steps = 0
    while (
        any(task.status != "Completed" for task in st.session_state.task_queue)
        and steps < 300
    ):
        if st.session_state.plan is None:
            generate_plan(algorithm, policy, auto_policy)
        try:
            execute_step(algorithm, policy, auto_policy)
        except RuntimeError as error:
            st.session_state.running = False
            st.session_state.status = f"Execution stopped: {error}"
            return
        steps += 1
    if steps >= 300:
        st.session_state.running = False
        st.session_state.status = "Execution stopped after the 300-action safety limit."


initialize_state()
environment: HouseEnvironment = st.session_state.environment
robot: Robot = st.session_state.robot
tracker: AnalyticsTracker = st.session_state.tracker

with st.sidebar:
    st.subheader("Run Configuration")
    selected_algorithm = SearchAlgorithm(
        st.selectbox(
            "Search algorithm",
            [algorithm.value for algorithm in SearchAlgorithm],
            index=4,
        )
    )
    selected_policy = Policy(
        st.selectbox("Cleaning policy", [policy.value for policy in Policy], index=3)
    )
    automatic_policy = st.toggle("Let AI select policy", value=False)

    st.divider()
    st.subheader("Execution")
    if st.button("Generate plan", type="primary", width="stretch"):
        generate_plan(selected_algorithm, selected_policy, automatic_policy)
        st.session_state.running = False
        st.session_state.status = "Plan generated. Ready to execute."

    if st.button("Execute next action", width="stretch"):
        if st.session_state.plan is None:
            generate_plan(selected_algorithm, selected_policy, automatic_policy)
        execute_step(selected_algorithm, selected_policy, automatic_policy)

    if st.button(
        "Run task queue",
        type="primary",
        width="stretch",
        disabled=not any(
            task.status != "Completed" for task in st.session_state.task_queue
        ),
    ):
        generate_plan(selected_algorithm, selected_policy, automatic_policy)
        run_task_queue(selected_algorithm, selected_policy, automatic_policy)
        st.rerun()

    pause_col, reset_col = st.columns(2)
    if pause_col.button("Pause", width="stretch"):
        st.session_state.running = False
        st.session_state.status = "Simulation paused."
    if reset_col.button("Reset", width="stretch"):
        reset_state()
        st.rerun()

    st.divider()
    st.subheader("Robot")
    st.progress(robot.battery / robot.max_battery, text=f"Battery {robot.battery:.1f}%")
    state_left, state_right = st.columns(2)
    state_left.metric("Cleaned", robot.cleaned_cells)
    state_right.metric("Dirt left", len(robot.knowledge.dirty_locations))
    st.caption(f"Position {robot.position}")

st.title("Autonomous Cleaning Strategy Planner")
st.caption(
    "Build a cleaning queue, let the AI schedule it, and inspect every route "
    "and decision."
)

active_plan: PlanDecision | None = st.session_state.plan
policy_label = active_plan.policy.value if active_plan else selected_policy.value
st.markdown(
    f"""
    <div class="status-strip">
      <span><strong>Status</strong> {st.session_state.status}</span>
      <span><strong>Position</strong> {robot.position}</span>
      <span><strong>Algorithm</strong> {selected_algorithm.value}</span>
      <span><strong>Policy</strong> {policy_label}</span>
      <span><strong>Tasks</strong> {sum(task.status != "Completed" for task in st.session_state.task_queue)} active</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tasks_tab, overview_tab, planning_tab, analytics_tab, knowledge_tab = st.tabs(
    ["Tasks", "Live Map", "Plan Details", "Analytics", "Explanations"]
)

with tasks_tab:
    st.subheader("Cleaning Queue")
    st.markdown(
        '<div class="section-note">Add rooms to clean, then generate a plan or run the complete queue.</div>',
        unsafe_allow_html=True,
    )
    form_col, queue_col = st.columns([0.85, 1.35], gap="large")
    with form_col:
        with st.form("add_cleaning_task", clear_on_submit=False):
            task_room = st.selectbox(
                "Room",
                list(environment.rooms),
                index=None,
                placeholder="Choose a room",
                key="task_room",
            )
            priority_col, duration_col = st.columns(2)
            task_priority = priority_col.select_slider(
                "Priority",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="Higher-priority rooms are favored by scheduling and utility scoring.",
            )
            task_duration = duration_col.number_input(
                "Duration (hours)",
                min_value=1,
                max_value=4,
                value=None,
                placeholder="e.g. 1",
            )
            start_col, end_col = st.columns(2)
            available_from = start_col.number_input(
                "Available from",
                min_value=8,
                max_value=16,
                value=None,
                placeholder="e.g. 8",
            )
            available_to = end_col.number_input(
                "Available until",
                min_value=9,
                max_value=18,
                value=None,
                placeholder="e.g. 17",
            )
            dirt_intensity = st.slider(
                "Expected dirt level", 0.1, 1.0, 0.8, 0.1
            )
            add_task = st.form_submit_button("Add to queue", type="primary", width="stretch")

        if add_task:
            duplicate = any(
                task.room_name == task_room and task.status != "Completed"
                for task in st.session_state.task_queue
            )
            if task_room is None:
                st.error("Choose a room before adding the task.")
            elif task_duration is None:
                st.error("Enter the expected cleaning duration.")
            elif available_from is None or available_to is None:
                st.error("Enter the room's available time window.")
            elif duplicate:
                st.warning(f"{task_room} already has an active task.")
            elif available_to <= available_from:
                st.error("Available until must be later than available from.")
            else:
                ensure_task_dirt(task_room, dirt_intensity)
                st.session_state.task_queue.append(
                    CleaningTask(
                        room_name=task_room,
                        duration=int(task_duration),
                        priority=task_priority,
                        battery_cost=0.0,
                        available_slots=set(
                            range(int(available_from), int(available_to))
                        ),
                    )
                )
                st.session_state.plan = None
                st.session_state.status = f"{task_room} added to the cleaning queue."
                st.rerun()

    with queue_col:
        if st.session_state.task_queue:
            task_table = pd.DataFrame(
                [
                    {
                        "Room": task.room_name,
                        "Priority": task.priority,
                        "Duration": f"{task.duration} hr",
                        "Available": (
                            f"{min(task.available_slots)}:00-"
                            f"{max(task.available_slots) + 1}:00"
                        ),
                        "Status": task.status,
                    }
                    for task in st.session_state.task_queue
                ]
            )
            st.dataframe(task_table, hide_index=True, width="stretch")
            pending_count = sum(
                task.status != "Completed" for task in st.session_state.task_queue
            )
            completed_count = len(st.session_state.task_queue) - pending_count
            queue_left, queue_mid, queue_right = st.columns([1, 1, 1.2])
            queue_left.metric("Active", pending_count)
            queue_mid.metric("Completed", completed_count)
            if queue_right.button("Clear completed", width="stretch"):
                st.session_state.task_queue = [
                    task
                    for task in st.session_state.task_queue
                    if task.status != "Completed"
                ]
                st.rerun()
        else:
            st.markdown(
                '<div class="queue-empty"><strong>No tasks yet</strong><br>'
                'Add a room using the form to begin planning.</div>',
                unsafe_allow_html=True,
            )

with overview_tab:
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.plotly_chart(
            grid_figure(
                environment,
                robot,
                active_plan.route if active_plan else None,
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
    with right:
        st.subheader("Current Objective")
        if active_plan and active_plan.selected_room:
            selected_assessment = next(
                item
                for item in active_plan.assessments
                if item.room_name == active_plan.selected_room
            )
            st.metric("Selected room", active_plan.selected_room)
            st.metric(
                "Target dirt probability",
                f"{selected_assessment.dirt_probability:.1%}",
            )
            st.metric(
                "Route length",
                active_plan.route.path_length if active_plan.route else 0,
            )
            st.metric("Schedule quality", f"{active_plan.schedule.quality:.0f}%")
        else:
            st.info("Add tasks, then select Generate plan in the sidebar.")
        st.caption(
            "Map legend: R robot | D dirt | X obstacle | C charger | "
            "* route | . explored"
        )
        st.subheader("Room Beliefs")
        beliefs = (
            pd.DataFrame(
                [
                    {
                        "Room": item.room_name,
                        "Dirt probability": item.dirt_probability,
                        "Cleaning need": item.cleaning_need,
                        "Utility": item.utility,
                    }
                    for item in active_plan.assessments
                ]
            )
            if active_plan
            else pd.DataFrame()
        )
        if not beliefs.empty:
            st.dataframe(
                beliefs.style.format(
                    {"Dirt probability": "{:.1%}", "Cleaning need": "{:.1%}", "Utility": "{:.2f}"}
                ),
                hide_index=True,
                width="stretch",
            )

with planning_tab:
    if not active_plan:
        st.info("Generate a plan to inspect route search and CSP scheduling.")
    else:
        route_col, schedule_col = st.columns(2, gap="large")
        with route_col:
            st.subheader("Search Trace")
            if active_plan.route:
                st.plotly_chart(
                    search_figure(active_plan.route),
                    width="stretch",
                    config={"displayModeBar": False},
                )
                st.caption(active_plan.route.explanation)
        with schedule_col:
            st.subheader("Constraint Schedule")
            durations = {
                name: room.cleaning_duration for name, room in environment.rooms.items()
            }
            durations.update(
                {
                    task.room_name: task.duration
                    for task in st.session_state.task_queue
                }
            )
            if active_plan.schedule.assignments:
                st.plotly_chart(
                    schedule_figure(active_plan.schedule.assignments, durations),
                    width="stretch",
                    config={"displayModeBar": False},
                )
            else:
                st.warning("No feasible schedule was produced.")
            for failure in active_plan.schedule.failures:
                st.caption(failure)

        st.subheader("Algorithm Comparison")
        if active_plan.target:
            comparison, _ = compare_algorithms(
                environment.graph, robot.position, active_plan.target
            )
            st.dataframe(
                comparison.style.format(
                    {
                        "Runtime (ms)": "{:.3f}",
                        "Peak Memory (KB)": "{:.1f}",
                        "Path Cost": "{:.2f}",
                    }
                ),
                hide_index=True,
                width="stretch",
            )

with analytics_tab:
    summary = tracker.summary(robot.battery, robot.cleaned_cells)
    columns = st.columns(5)
    labels = [
        ("Area cleaned", f"{summary['Total Area Cleaned']:.0f} cells"),
        ("Efficiency", f"{summary['Cleaning Efficiency']:.2f} cells/%"),
        ("Battery used", f"{summary['Battery Consumption']:.1f}%"),
        ("Runtime", f"{summary['Runtime']:.1f}s"),
        ("Prediction accuracy", f"{summary['Prediction Accuracy']:.1%}"),
    ]
    for column, (label, value) in zip(columns, labels):
        column.metric(label, value)
    history = tracker.frame()
    if history.empty:
        st.info("Execute actions to populate time-series analytics.")
    else:
        battery_chart = px.line(
            history,
            x="Step",
            y="Battery",
            markers=True,
            title="Battery Consumption",
            color_discrete_sequence=["#087e8b"],
        )
        cleaned_chart = px.bar(
            history,
            x="Step",
            y="Cleaned Cells",
            title="Cumulative Area Cleaned",
            color_discrete_sequence=["#f59e0b"],
        )
        left, right = st.columns(2)
        left.plotly_chart(battery_chart, width="stretch")
        right.plotly_chart(cleaned_chart, width="stretch")
        st.dataframe(history, hide_index=True, width="stretch")

with knowledge_tab:
    st.subheader("Decision Explanations")
    explanations = active_plan.explanations if active_plan else []
    if explanations:
        for explanation in explanations[-8:]:
            st.markdown(
                f'<div class="explanation">{explanation}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("Explanations appear after a plan is generated.")

    with st.expander("Complete reasoning log", expanded=False):
        st.code("\n".join(robot.knowledge.reasoning_log) or "No actions recorded.")

    with st.expander("Robot knowledge base", expanded=False):
        kb_left, kb_right = st.columns(2)
        kb_left.write("**Visited locations**")
        kb_left.code(str(sorted(robot.knowledge.visited_locations)))
        kb_left.write("**Known obstacles**")
        kb_left.code(str(sorted(robot.knowledge.obstacles)))
        kb_right.write("**Known dirty locations**")
        kb_right.code(str(sorted(robot.knowledge.dirty_locations)))
        kb_right.write("**Battery belief**")
        kb_right.code(f"{robot.knowledge.battery_level:.1f}%")

    with st.expander("AI concepts and PEAS reference", expanded=False):
        peas = environment.peas()
        st.dataframe(
            pd.DataFrame(
                [
                    {"Component": key, "Definition": ", ".join(values)}
                    for key, values in peas.items()
                ]
            ),
            hide_index=True,
            width="stretch",
        )
        concept_columns = st.columns(3)
        concept_columns[0].markdown(
            "**Search**\n\nBFS, DFS, UCS, Greedy Best-First, and A* expose their "
            "frontier, explored set, path, cost, and performance statistics."
        )
        concept_columns[1].markdown(
            "**Constraint Reasoning**\n\nMRV, degree, LCV, forward checking, arc "
            "consistency, backtracking, and min-conflicts produce the timetable."
        )
        concept_columns[2].markdown(
            "**Uncertainty & Decisions**\n\nBayesian sensor fusion and temporal "
            "prediction feed utility-based policy and room selection."
        )
