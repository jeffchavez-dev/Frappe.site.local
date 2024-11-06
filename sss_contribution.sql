SELECT
    id.identification_number AS 'SSS ID No.',
    CONCAT(COALESCE(last_name, ''), ', ', COALESCE(first_name, ''), COALESCE(middle_name, '')) AS `Full Name:Data:250`,
    COALESCE(SUM(sd.amount), 0) + COALESCE(SUM(sder.amount), 0) AS `SS:Currency:150`,
    COALESCE(SUM(sdec.amount), 0) AS `EC:Currency:150`,
    COALESCE(SUM(sd.amount), 0) + COALESCE(SUM(sder.amount), 0) + COALESCE(SUM(sdec.amount), 0) AS `Total Contributions:Currency:150`

    For HHI
    COALESCE(SUM(sd.amount), 0) AS `Employee Share:Currency:150`,
    COALESCE(SUM(sder.amount), 0) AS `Employer Share:Currency:150`,
    COALESCE(SUM(sdec.amount), 0) AS `ECola:Currency:150`,
    COALESCE(SUM(sd.amount), 0) + COALESCE(SUM(sder.amount), 0) + COALESCE(SUM(sdec.amount), 0) AS `Total Contributions:Currency:150`



FROM
    `tabEmployee` emp
LEFT JOIN
    `tabEmployee Identification Document` id ON
        id.parent = emp.name AND
        id.type = 'SSS ID'
INNER JOIN
    `tabSalary Slip` ss ON
        ss.employee = emp.name AND
        MONTHNAME(ss.posting_date) = %(month)s AND
        YEAR(ss.posting_date) = %(year)s
LEFT JOIN
    `tabSalary Detail` sd ON
        sd.abbr = 'PH_SSS' AND
        sd.parent = ss.name
LEFT JOIN
    `tabSalary Detail` sder ON
        sder.abbr = 'PH_SSS_ER' AND
        sder.parent = ss.name
LEFT JOIN
    `tabSalary Detail` sdec ON
        sdec.abbr = 'PH_SSS_EC' AND
        sdec.parent = ss.name
GROUP BY
    MONTHNAME(ss.posting_date), YEAR(ss.posting_date), emp.name
HAVING
    SUM(sd.amount) > 0 OR SUM(sder.amount) > 0;