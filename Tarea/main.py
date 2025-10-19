import typer
import uuid
from rich.console import Console
from rich.table import Table
from typing import Literal
from rich import print
from connection.connect_database import connect_database
from helpers.status_colors import status_colored

# Conexión a la base de datos
conn = connect_database("./src/database/todo.db")

app = typer.Typer()
table = Table("UUID", "Name", "Description", "Status", show_lines=True)
console = Console()

STATUS = Literal["COMPLETED", "PENDING", "IN_PROGRESS"]

@app.command(short_help="Create on task")
def create(name: str, description: str, status: STATUS):
  if conn:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO TASKS(uuid, name, description, status) VALUES(?, ?, ?, ?)",
        (str(uuid.uuid4()), name, description, status, )
    )
    conn.commit()
    conn.close()
    print("One task have been [bold green]created[/bold green]")

@app.command(short_help="List all tasks")
def list():
  if conn:
    cursor = conn.cursor()
    results = cursor.execute(
        "SELECT uuid, name, description, status FROM tasks"
    )
    for uuid, name, description, status in results.fetchall():
      status_with_color = status_colored(status)

      table.add_row(uuid, name, description, status_with_color)
    conn.close()

  table.caption = "List all tasks"
  console.print(table)

@app.command(short_help="Update one task")
def update(uuid_task: str, name: str = None, description: str = None, status: STATUS = None):
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TASKS WHERE uuid = ?", (uuid_task,))
        task = cursor.fetchone()
        if not task:
            print(f"[red]No se encontró ninguna tarea con ese UUID.[/red]")
            conn.close()
            return

        new_name = name if name else task[1]
        new_description = description if description else task[2]
        new_status = status if status else task[3]

        cursor.execute("""
            UPDATE TASKS 
            SET name = ?, description = ?, status = ?
            WHERE uuid = ?
        """, (new_name, new_description, new_status, uuid_task))
        conn.commit()
        conn.close()
        print("[green]Tarea actualizada correctamente.[/green]")

  
@app.command(short_help="Delete one task")
def delete(uuid_task: str):
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TASKS WHERE uuid = ?", (uuid_task,))
        task = cursor.fetchone()
        if not task:
            print(f"[red]No se encontró ninguna tarea con ese UUID.[/red]")
            conn.close()
            return

        cursor.execute("DELETE FROM TASKS WHERE uuid = ?", (uuid_task,))
        conn.commit()
        conn.close()
        print("[green]Tarea eliminada correctamente.[/green]")



if __name__ == "__main__":
  app()
