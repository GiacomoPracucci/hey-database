from src.config.models.metadata import TableMetadata, EnhancedTableMetadata


class TableMetadataExtractor:
    def extract_metadata(self, table_name: str) -> TableMetadata:
        """
        Estrae i metadati base di una tabella.

        Args:
            table_name: Nome della tabella
        Returns:
            TableMetadata: Metadati base della tabella
        """
        # 1. estrazione delle info sulle colonne
        columns = self._get_table_columns_metadata(table_name)

        # 2. estrazione delle info sulle pks
        primary_keys = self._get_table_pk_metadata(table_name)

        # 3. estrazione delle info sulle fks
        foreign_keys = self._get_table_fk_metadata(table_name)

        # 4. row count della tabella
        row_count = self._get_row_count(table_name)

        return TableMetadata(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            row_count=row_count,
        )
