from pathlib import Path

from ontobdc.run.core.port.contex import CliContextPort, CliContextStrategyPort


class NormalizedIfcPathStrategy(CliContextStrategyPort):
    def execute(self, context: CliContextPort) -> CliContextPort:
        norm_ifc_path = context.get_parameter_value("normalized_ifc_path")
        if isinstance(norm_ifc_path, str) and norm_ifc_path:
            context.add_parameter(
                "normalized_ifc_path",
                {
                    "value": str(Path(norm_ifc_path).expanduser().resolve()),
                    "uri": "org.local.domain.context.strategy.parameter.ifc_path.normalized",
                },
            )

        return context
