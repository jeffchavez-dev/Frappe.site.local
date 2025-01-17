SELECT 
       `Campus:Data:150`, 
       `RowType` AS `Items`, 
       `Total Students:Int:150`, 
       `Paying Students:Int:150`, 
       `Non-Paying Student:Int:150`, 
       `Availed IEE:Int:150`, 
       `Regular:Int:150`, 
       `Late Enrollees:Int:150`, 
       `May - July:Currency/PHP:150`, 
       `August:Currency/PHP:150`, 
       `September:Currency/PHP:150`, 
       `October:Currency/PHP:150`, 
       `November:Currency/PHP:150`, 
       `December:Currency/PHP:150`, 
       `January:Currency/PHP:150`, 
       `February:Currency/PHP:150`, 
       `March:Currency/PHP:150`, 
       `April:Currency/PHP:150`, 
       `May:Currency/PHP:150`, 
       `IEE Amount:Currency/PHP:150`, 
       `Total Regular Enrollees:Currency/PHP:150`, 
       `Total with IEE:Currency/PHP:150`, 
       `Total Bond:Currency/PHP:150`, 
       `Total Without Bond:Currency/PHP:150`
FROM (
    -- Original query for campus data
    SELECT `source`.`Campus:Data:150` AS `Campus:Data:150`,
      SUM(
        CASE
          WHEN (`source`.`PE Docstatus Aggregate` <> 0)
          OR (`source`.`PE Docstatus Aggregate` IS NULL) THEN 1
          ELSE 0.0
        END
      ) AS `Total Students:Int:150`,
      SUM(
        CASE
          WHEN (`source`.`Paying Student Aggregate` <> 0)
          OR (`source`.`Paying Student Aggregate` IS NULL) THEN 1
          ELSE 0.0
        END
      ) AS `Paying Students:Int:150`,
      SUM(
        CASE
          WHEN (`source`.`Non-Paying Aggregate` <> 0)
          OR (`source`.`Non-Paying Aggregate` IS NULL) THEN 1
          ELSE 0.0
        END
      ) AS `Non-Paying Student:Int:150`,
      SUM(
        CASE
          WHEN (`source`.`Availed IEE Aggregate` <> 0)
          OR (`source`.`Availed IEE Aggregate` IS NULL) THEN 1
          ELSE 0.0
        END
      ) AS `Availed IEE:Int:150`,
      SUM(
        CASE
          WHEN (`source`.`Regular Student Aggregate` <> 0)
          OR (`source`.`Regular Student Aggregate` IS NULL) THEN 1
          ELSE 0.0
        END
      ) AS `Regular:Int:150`,
      SUM(
        CASE
          WHEN (`source`.`Late Student Aggregate` <> 0)
          OR (`source`.`Late Student Aggregate` IS NULL) THEN 1
          ELSE 0.0
        END
      ) AS `Late Enrollees:Int:150`,
      SUM(`source`.`May to July OF Aggregate`) AS `May - July:Currency/PHP:150`,
      SUM(`source`.`August OF Aggregate`) AS `August:Currency/PHP:150`,
      SUM(`source`.`September OF Aggregate`) AS `September:Currency/PHP:150`,
      SUM(`source`.`October OF Aggregate`) AS `October:Currency/PHP:150`,
      SUM(`source`.`November OF Aggregate`) AS `November:Currency/PHP:150`,
      SUM(`source`.`December OF Aggregate`) AS `December:Currency/PHP:150`,
      SUM(`source`.`January OF Aggregate`) AS `January:Currency/PHP:150`,
      SUM(`source`.`February OF Aggregate`) AS `February:Currency/PHP:150`,
      SUM(`source`.`March OF Aggregate`) AS `March:Currency/PHP:150`,
      SUM(`source`.`April OF Aggregate`) AS `April:Currency/PHP:150`,
      SUM(`source`.`May OF Aggregate`) AS `May:Currency/PHP:150`,
      SUM(`source`.`IEE Amount Aggregate`) AS `IEE Amount:Currency/PHP:150`,
      SUM(`source`.`Regular Enrollees OA Aggregate`) AS `Total Regular Enrollees:Currency/PHP:150`,
      SUM(`source`.`Total with IEE Aggregate`) AS `Total with IEE:Currency/PHP:150`,
      SUM(`source`.`Total Bond Aggregate`) AS `Total Bond:Currency/PHP:150`,
      SUM(`source`.`Total Without Bond Aggregate`) AS `Total Without Bond:Currency/PHP:150`,
      1 AS `RowNumber`, -- Main row comes first
      'Expected Total Collection' AS `RowType` -- Identifier for main rows
    FROM (
        -- Subquery for original data
        SELECT `tabStudent`.`name` AS `name`,
          SUM(
            CASE
              WHEN (
                `TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN 1
              ELSE 0.0
            END
          ) AS `Availed IEE Aggregate`,
          MIN(`TabProgram Enrollment`.`campus`) AS `Campus:Data:150`,
          SUM(
            CASE
              WHEN (
                NOT (
                  `TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
                )
                OR (
                  `TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
                )
              )
              AND (
                `TabProgram Enrollment`.`fees_due_schedule_template` IS NOT NULL
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN 1
              ELSE 0.0
            END
          ) AS `Regular Student Aggregate`,
          SUM(
            CASE
              WHEN (
                `TabProgram Enrollment`.`student_category` = 'Non-paying Student'
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1) THEN 1
              ELSE 0.0
            END
          ) AS `Non-Paying Aggregate`,
          SUM(
            CASE
              WHEN (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1) THEN 1
              ELSE 0.0
            END
          ) AS `Paying Student Aggregate`,
          SUM(
            CASE
              WHEN (
                `TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              )
              AND (`TabFees`.`student_cart_item` IS NULL) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `IEE Amount Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 8)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `August OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 9)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `September OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 10)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `October OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 11)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `November OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 12)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `December OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 1)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `January OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 2)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `February OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 3)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `March OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 4)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `April OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 5)
              AND (
                YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `May OF Aggregate`,
          SUM(
            CASE
              WHEN (MONTH(`TabFees`.`due_date`) = 5)
              OR (MONTH(`TabFees`.`due_date`) = 6)
              OR (
                (MONTH(`TabFees`.`due_date`) = 7)
                AND (
                  YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
                )
                AND (`TabProgram Enrollment`.`docstatus` = 1)
                AND (`TabFees`.`docstatus` = 1)
                AND (`TabFees`.`student_cart_item` IS NULL)
                AND (
                  (
                    `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                  )
                  OR (
                    `TabProgram Enrollment`.`student_category` IS NULL
                  )
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `May to July OF Aggregate`,
          SUM(
            CASE
              WHEN (
                (
                  NOT (
                    `TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
                  )
                  OR (
                    `TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
                  )
                )
                OR (
                  `TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
                )
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              )
              AND (`TabFees`.`student_cart_item` IS NULL) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `Total with IEE Aggregate`,
          SUM(
            CASE
              WHEN (
                NOT (
                  `TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
                )
                OR (
                  `TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
                )
              )
              AND (
                `TabProgram Enrollment`.`fees_due_schedule_template` IS NOT NULL
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              )
              AND (`TabFees`.`student_cart_item` IS NULL) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `Regular Enrollees OA Aggregate`,
          SUM(
            CASE
              WHEN (
                `TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN 1
              ELSE 0.0
            END
          ) AS `Late Student Aggregate`,
          SUM(
            CASE
              WHEN (
                `TabFee Component`.`fees_category` LIKE '%%Bond%%'
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `Total Bond Aggregate`,
          SUM(
            CASE
              WHEN (
                NOT (
                  `TabFee Component`.`fees_category` LIKE '%%Bond%%'
                )
                OR (`TabFee Component`.`fees_category` IS NULL)
              )
              AND (`TabProgram Enrollment`.`docstatus` = 1)
              AND (`TabFees`.`docstatus` = 1)
              AND (`TabFees`.`student_cart_item` IS NULL)
              AND (
                (
                  `TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
                )
                OR (
                  `TabProgram Enrollment`.`student_category` IS NULL
                )
              ) THEN `TabFee Component`.`amount`
              ELSE 0.0
            END
          ) AS `Total Without Bond Aggregate`,
          SUM(
            CASE
              WHEN `TabProgram Enrollment`.`docstatus` = 1 THEN 1
              ELSE 0.0
            END
          ) AS `PE Docstatus Aggregate`
          
        FROM `tabStudent`
          LEFT JOIN `tabProgram Enrollment` AS `TabProgram Enrollment` ON `tabStudent`.`name` = `TabProgram Enrollment`.`student`
          LEFT JOIN `tabFees` AS `TabFees` ON `tabStudent`.`name` = `TabFees`.`student`
          LEFT JOIN `tabAcademic Year` AS `TabAcademic Year` ON `TabProgram Enrollment`.`academic_year` = `TabAcademic Year`.`name`
          LEFT JOIN `tabFee Component` AS `TabFee Component` ON `TabFees`.`name` = `TabFee Component`.`parent`
        WHERE `TabProgram Enrollment`.`academic_year` = %(academic_year)s OR %(academic_year)s IS NULL
        GROUP BY `tabStudent`.`name`
    ) AS `source`
    GROUP BY `source`.`Campus:Data:150`

    UNION ALL

    -- Add sub-rows for each campus
    SELECT `Campus:Data:150`,
           NULL AS `Total Students:Int:150`,
           NULL AS `Paying Students:Int:150`,
           NULL AS `Non-Paying Student:Int:150`,
           NULL AS `Availed IEE:Int:150`,
           NULL AS `Regular:Int:150`,
           NULL AS `Late Enrollees:Int:150`,
           NULL AS `May - July:Currency/PHP:150`,
           NULL AS `August:Currency/PHP:150`,
           NULL AS `September:Currency/PHP:150`,
           NULL AS `October:Currency/PHP:150`,
           NULL AS `November:Currency/PHP:150`,
           NULL AS `December:Currency/PHP:150`,
           NULL AS `January:Currency/PHP:150`,
           NULL AS `February:Currency/PHP:150`,
           NULL AS `March:Currency/PHP:150`,
           NULL AS `April:Currency/PHP:150`,
           NULL AS `May:Currency/PHP:150`,
           NULL AS `IEE Amount:Currency/PHP:150`,
           NULL AS `Total Regular Enrollees:Currency/PHP:150`,
           NULL AS `Total with IEE:Currency/PHP:150`,
           NULL AS `Total Bond:Currency/PHP:150`,
           NULL AS `Total Without Bond:Currency/PHP:150`,
           ROW_NUMBER() OVER (PARTITION BY `Campus:Data:150` ORDER BY `RowType`) + 1 AS `RowNumber`, -- Sub-rows come after main row
           `RowType`
    FROM (
        SELECT DISTINCT `Campus:Data:150`
        FROM (
            -- Subquery to get distinct campuses
            SELECT MIN(`TabProgram Enrollment`.`campus`) AS `Campus:Data:150`
            FROM `tabStudent`
              LEFT JOIN `tabProgram Enrollment` AS `TabProgram Enrollment` ON `tabStudent`.`name` = `TabProgram Enrollment`.`student`
            WHERE `TabProgram Enrollment`.`academic_year` = %(academic_year)s OR %(academic_year)s IS NULL
            GROUP BY `tabStudent`.`name`
        ) AS `campuses`
    ) AS `distinct_campuses`
    CROSS JOIN (
        SELECT 'Current Actual Collection' AS `RowType`
        UNION ALL
        SELECT 'Account Receivable'
        UNION ALL
        SELECT 'Expenses'
        UNION ALL
        SELECT 'Projected Cash'
        UNION ALL
        SELECT 'Actual Cash'
    ) AS `additional_rows`
) AS `final_data`
ORDER BY `Campus:Data:150`, `RowNumber`, `RowType`;
