with date_spine as (

    select
        dateadd(
            day,
            seq4(),
            to_date('2016-01-01')
        ) as date_day

    from table(generator(rowcount => 1827))

),

final as (

    select

        /* Primary Key */

        to_number(
            to_char(date_day, 'YYYYMMDD')
        ) as date_id,

        /* Date */

        date_day as date,

        /* Year */

        year(date_day) as year,

        /* Semester */

        case
            when month(date_day) <= 6 then 1
            else 2
        end as semester,

        /* Quarter */

        quarter(date_day) as quarter,

        /* Month */

        month(date_day) as month_number,

        monthname(date_day) as month_name,

        /* Week */

        week(date_day) as week_of_year,

        ceil(day(date_day) / 7.0) as week_of_month,

        /* Day */

        dayofyear(date_day) as day_of_year,

        day(date_day) as day_of_month,

        dayofweek(date_day) as day_of_week,

        dayname(date_day) as day_name_of_week,

        /* Season (Brazil / Southern Hemisphere) */

        case
            when month(date_day) in (12, 1, 2)
                then 'Summer'

            when month(date_day) in (3, 4, 5)
                then 'Autumn'

            when month(date_day) in (6, 7, 8)
                then 'Winter'

            when month(date_day) in (9, 10, 11)
                then 'Spring'
        end as season,

        /* Weekend */

        case
            when dayofweek(date_day) in (0, 6)
                then true
            else false
        end as is_weekend,

        /* Month Flags */

        case
            when date_day = date_trunc('month', date_day)
                then true
            else false
        end as is_month_start,

        case
            when date_day = last_day(date_day)
                then true
            else false
        end as is_month_end,

        /* Quarter Flags */

        case
            when date_day = date_trunc('quarter', date_day)
                then true
            else false
        end as is_quarter_start,

        case
            when date_day =
                 dateadd(
                     day,
                     -1,
                     dateadd(
                         quarter,
                         1,
                         date_trunc('quarter', date_day)
                     )
                 )
                then true
            else false
        end as is_quarter_end

    from date_spine

)

select *
from final