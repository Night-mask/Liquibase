import os
import sys
from datetime import datetime, timezone

# Directory where generated changelog XMLs will be stored
CHANGELOG_DIR = "./changelog/child"

# GitHub metadata
GITHUB_ACTOR = os.getenv("GITHUB_ACTOR", "github-actions")
GITHUB_SHA = os.getenv("GITHUB_SHA", "local")[:7]

def generate_changelog(sql_file: str):
    """
    Generates a Liquibase XML changelog for a given SQL file.
    """

    os.makedirs(CHANGELOG_DIR, exist_ok=True)

    # Timezone-aware UTC timestamp (Python 3.12+ safe)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    sql_name = os.path.basename(sql_file)
    changeset_id = f"{timestamp}-{GITHUB_SHA}"

    changelog_name = f"{timestamp}_{sql_name.replace('.sql', '.changelog.xml')}"
    changelog_path = os.path.join(CHANGELOG_DIR, changelog_name)

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="
      http://www.liquibase.org/xml/ns/dbchangelog
      http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.27.xsd">

    <changeSet id="{changeset_id}" author="{GITHUB_ACTOR}">
        <sqlFile
            path="../{sql_name}"
            relativeToChangelogFile="true"
            splitStatements="true"
            stripComments="true"/>
    </changeSet>

</databaseChangeLog>
"""

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated changelog: {changelog_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python SCRIPT.py <sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]

    if not os.path.exists(sql_file):
        print(f"SQL file not found: {sql_file}")
        sys.exit(1)

    generate_changelog(sql_file)


if __name__ == "__main__":
    main()
