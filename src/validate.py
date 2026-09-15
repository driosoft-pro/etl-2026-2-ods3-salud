import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_foreign_keys(fact_df: pd.DataFrame, dim_dfs: dict, fk_columns: dict) -> list:
    errors = []
    for fk_col, (dim_name, dim_df, dim_sk) in fk_columns.items():
        if fk_col not in fact_df.columns:
            errors.append(f"FK column '{fk_col}' not found in fact table")
            continue
        null_count = fact_df[fk_col].isna().sum()
        if null_count > 0:
            errors.append(f"FK '{fk_col}' has {null_count} null values")
        if dim_df is not None and dim_sk in dim_df.columns:
            invalid = ~fact_df[fk_col].dropna().isin(dim_df[dim_sk])
            if invalid.any():
                errors.append(f"FK '{fk_col}' has {invalid.sum()} values not present in {dim_name}")
    return errors

def validate_measures(fact_df: pd.DataFrame, measure_columns: list) -> list:
    errors = []
    for col in measure_columns:
        if col not in fact_df.columns:
            errors.append(f"Measure column '{col}' not found in fact table")
            continue
        null_count = fact_df[col].isna().sum()
        if null_count > 0:
            errors.append(f"Measure '{col}' has {null_count} null values")
        negative = (fact_df[col] < 0).sum()
        if negative > 0:
            errors.append(f"Measure '{col}' has {negative} negative values")
    return errors

def validate_no_duplicates(fact_df: pd.DataFrame, key_columns: list) -> list:
    errors = []
    existing = [c for c in key_columns if c in fact_df.columns]
    if existing:
        dupes = fact_df.duplicated(subset=existing, keep=False)
        if dupes.any():
            errors.append(f"Fact table has {dupes.sum()} duplicate rows on {existing}")
    return errors

def validate_raw_affiliates(df: pd.DataFrame) -> list:
    errors = []
    required = ['department_code', 'department', 'municipality_code', 'municipality',
                'regime_id', 'year', 'month', 'num_persons']
    for col in required:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    if 'num_persons' in df.columns:
        vals = pd.to_numeric(df['num_persons'].str.replace('.', '', regex=False), errors='coerce')
        if (vals < 0).sum() > 0:
            errors.append("num_persons contains negative values")
    if 'regime_id' in df.columns:
        valid = {'S', 'E', 'C', 'I'}
        invalid = set(df['regime_id'].unique()) - valid
        if invalid:
            errors.append(f"Invalid regime codes: {invalid}")
    return errors

def validate_sum_consistency(fact_df: pd.DataFrame, original_total: int,
                              measure_col: str = 'numero_afiliados',
                              tolerance_pct: float = 0.01) -> list:
    errors = []
    fact_total = fact_df[measure_col].sum()
    diff = abs(fact_total - original_total)
    threshold = original_total * tolerance_pct
    if diff > threshold:
        errors.append(
            f"Sum mismatch: fact={fact_total:,} vs original={original_total:,} "
            f"(diff={diff:,}, threshold={threshold:,.0f})"
        )
    return errors

def run_all_validations(fact_affiliates: pd.DataFrame, fact_capacity: pd.DataFrame,
                         dim_time: pd.DataFrame, dim_geografia: pd.DataFrame,
                         dim_regime: pd.DataFrame, dim_facility: pd.DataFrame,
                         dim_capacity_type: pd.DataFrame,
                         original_total: int = None) -> dict:
    all_errors = {}
    
    fk_errors = validate_foreign_keys(
        fact_affiliates, {},
        {
            'sk_time': ('dim_time', dim_time, 'sk_time'),
            'sk_geografia': ('dim_geografia', dim_geografia, 'sk_geografia'),
            'sk_regime': ('dim_regime', dim_regime, 'sk_regime'),
        }
    )
    all_errors['fact_affiliates_fk'] = fk_errors
    
    measure_errors = validate_measures(fact_affiliates, ['numero_afiliados'])
    all_errors['fact_affiliates_measures'] = measure_errors
    
    dupe_errors = validate_no_duplicates(
        fact_affiliates, ['sk_time', 'sk_geografia', 'sk_regime']
    )
    all_errors['fact_affiliates_dupes'] = dupe_errors
    
    if original_total is not None:
        sum_errors = validate_sum_consistency(fact_affiliates, original_total)
        all_errors['fact_affiliates_sum'] = sum_errors
    
    capacity_fk = validate_foreign_keys(
        fact_capacity, {},
        {
            'sk_time': ('dim_time', dim_time, 'sk_time'),
            'sk_facility': ('dim_facility', dim_facility, 'sk_facility'),
            'sk_capacity_type': ('dim_capacity_type', dim_capacity_type, 'sk_capacity_type'),
        }
    )
    all_errors['fact_capacity_fk'] = capacity_fk
    
    total_errors = sum(len(v) for v in all_errors.values())
    if total_errors == 0:
        logger.info("All validations passed successfully")
    else:
        logger.warning(f"Validation completed with {total_errors} errors")
        for key, errs in all_errors.items():
            if errs:
                for e in errs:
                    logger.error(f"  [{key}] {e}")
    
    return all_errors
