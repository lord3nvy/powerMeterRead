CREATE OR ALTER PROCEDURE sp_PowerUsageMergeToMain
AS

BEGIN
    SET NOCOUNT ON;

    -- Merge data from v_raw_PowerUsage_Transform to PowerUsage
    MERGE INTO PowerUsage AS target
    USING v_raw_PowerUsage_Transform AS source
        ON  target.ESIID = source.ESIID
        AND target.USAGE_DATE = source.USAGE_DATE
        AND target.USAGE_START_TIME = source.USAGE_START_TIME
        AND target.USAGE_END_TIME = source.USAGE_END_TIME
    WHEN MATCHED THEN
        UPDATE SET 
            target.USAGE_KWH = source.USAGE_KWH,
            target.ESTIMATED_ACTUAL = source.ESTIMATED_ACTUAL,
            target.CONSUMPTION_SURPLUSGENERATION = source.CONSUMPTION_SURPLUSGENERATION,
            target.MergeDateStamp = GETDATE()
    WHEN NOT MATCHED THEN
        INSERT (ESIID, USAGE_DATE, REVISION_DATE, USAGE_START_TIME, USAGE_END_TIME, USAGE_KWH, ESTIMATED_ACTUAL, CONSUMPTION_SURPLUSGENERATION, MergeDateStamp)
        VALUES (source.ESIID, source.USAGE_DATE, source.REVISION_DATE, source.USAGE_START_TIME, source.USAGE_END_TIME, source.USAGE_KWH, source.ESTIMATED_ACTUAL, source.CONSUMPTION_SURPLUSGENERATION, GETDATE());


END;