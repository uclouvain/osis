CREATE OR REPLACE FUNCTION update_unversioned_fields_of_group_years() RETURNS TRIGGER AS
$$
BEGIN
    -- Check if it is a root group => having a reference into program_management_educationgroupversion
    IF EXISTS(
            SELECT *
            FROM public.program_management_educationgroupversion
            WHERE root_group_id = OLD.id
        ) THEN
        WITH offer_fields AS (
            SELECT egy.id, egy.acronym, egy.title, egy.title_english
            FROM public.base_educationgroupyear egy
            JOIN public.program_management_educationgroupversion egv
            ON egv.offer_id = egy.id AND egv.root_group_id = OLD.id
        ),
         group_ids AS (
             SELECT gy.id
             FROM public.education_group_groupyear gy
             JOIN public.program_management_educationgroupversion egv ON egv.root_group_id = gy.id
             WHERE egv.offer_id = (SELECT id FROM offer_fields)
         )
        UPDATE public.education_group_groupyear gy
        SET (title_fr, title_en, acronym) = (SELECT title, title_english, acronym FROM offer_fields)
        WHERE id IN (SELECT * FROM group_ids);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS UPDATED_EDUCATION_GROUP_GROUPYEAR ON public.education_group_groupyear;
CREATE TRIGGER UPDATED_EDUCATION_GROUP_GROUPYEAR
    AFTER UPDATE OR INSERT
    ON public.education_group_groupyear
    FOR EACH ROW
    -- To avoid that the trigger is fired by itself or other trigger
    WHEN (pg_trigger_depth() < 1)
EXECUTE PROCEDURE update_unversioned_fields_of_group_years();
