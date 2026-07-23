import csv
from pathlib import Path
from uuid import uuid4
from config import settings
class CsvExportService:

    def export(self, iterator):
        filename = f"{uuid4()}.csv"

        # Use the configured download directory instead of the hardcoded typo
        output = Path(settings.DOWNLOAD_DIR) / filename

        # Create the directory if it doesn't exist
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w", newline="", encoding="utf8") as fp:
            writer = csv.writer(fp)
            header_written = False
            rows = 0
            for row in iterator:
                if not header_written:
                    writer.writerow(row.keys())
                    header_written = True

                writer.writerow(list(row.values()))
                rows += 1

        return rows, str(output)