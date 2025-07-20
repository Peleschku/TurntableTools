from . import v1 as TurnTable

if TurnTable:
    PluginRegistry = [
        ("SuperTool", 2, "TurnTable",
            (TurnTable.TurnTableNode,
                    TurnTable.GetEditor)),
    ]