from __future__ import annotations
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint
import jarvis.memory as mem
from jarvis.agent import GRAPH, AgentState
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)
console = Console()


def run_turn(user_input: str, voice_mode: bool = False) -> str:
    mem.add_episode("user", user_input)
    state: AgentState = {
        "user_input": user_input,
        "history": [],
        "memories": [],
        "tool_results": [],
        "final_response": None,
        "retry_count": 0,
        "awaiting_confirm": None,
    }

    with console.status("[bold cyan]Thinking...[/]"):
        result = GRAPH.invoke(state)

    # Handle confirmation request
    if result.get("awaiting_confirm"):
        msg = result["awaiting_confirm"]
        console.print(Panel(f"[yellow]{msg}[/yellow]\\nProceed? (y/n)", title="Confirmation Required"))
        answer = Prompt.ask("").strip().lower()
        if answer in ("y", "yes"):
            # Re-run with confirmed flag injected
            new_input = user_input + " [CONFIRMED by user]"
            return run_turn(new_input, voice_mode)
        else:
            response = "Cancelled."
            mem.add_episode("assistant", response)
            return response

    response = result.get("final_response") or "Done."
    mem.add_episode("assistant", response, tools_called=[r["tool"] for r in result.get("tool_results", [])])
    return response


def start_cli():
    mem.init_db()
    console.print(Panel.fit(
        "[bold cyan]JARVIS[/bold cyan] — Offline AI Operator\\n"
        "[dim]Type your command. 'exit' to quit. 'voice' to switch to voice mode.[/dim]",
        border_style="cyan"
    ))
    while True:
        try:
            user_input = Prompt.ask("[bold]>[/bold]").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]Goodbye.[/dim]")
                break
            if user_input.lower() == "voice":
                start_voice()
                break
            response = run_turn(user_input)
            console.print(Panel(response, title="[bold cyan]Jarvis[/bold cyan]", border_style="cyan"))
        except KeyboardInterrupt:
            console.print("\\n[dim]Interrupted.[/dim]")
            break


def start_voice():
    from jarvis.voice.stt import record_and_transcribe
    from jarvis.voice.tts import speak
    mem.init_db()
    console.print(Panel.fit("[bold cyan]JARVIS — Voice Mode[/bold cyan]\\n[dim]Speak to Jarvis. Say 'exit' to quit.[/dim]"))
    while True:
        try:
            console.print("[dim]Listening...[/dim]")
            text = record_and_transcribe()
            if not text:
                continue
            console.print(f"[dim]You: {text}[/dim]")
            if text.lower().strip() in ("exit", "quit", "stop"):
                speak("Goodbye.")
                break
            response = run_turn(text, voice_mode=True)
            console.print(Panel(response, title="[bold cyan]Jarvis[/bold cyan]"))
            speak(response)
        except KeyboardInterrupt:
            console.print("\\n[dim]Interrupted.[/dim]")
            break
