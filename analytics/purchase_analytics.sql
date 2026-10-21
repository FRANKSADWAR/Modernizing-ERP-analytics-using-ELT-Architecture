WITH 
    purchased_raw_materials AS (
        SELECT 
            `tabPurchase Invoice Item`.parent,
            `tabPurchase Invoice`.posting_date,
            `tabPurchase Invoice Item`.item_code,
            `tabPurchase Invoice Item`.item_name,
            `tabPurchase Invoice Item`.item_group,
            `tabPurchase Invoice Item`.qty,
            `tabPurchase Invoice Item`.rate,
            `tabPurchase Invoice Item`.uom
        FROM `tabPurchase Invoice Item` 
            INNER JOIN `tabPurchase Invoice` ON `tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
            INNER JOIN `tabItem` AS itm ON `tabPurchase Invoice Item`.item_code = itm.name
        WHERE `tabPurchase Invoice`.docstatus = 1 
            AND `tabPurchase Invoice`.is_return = 0
            AND itm.item_group = 'RAW MATERIALS'
            AND {{ date }}
    ),
    purchased_item_list AS (
        SELECT 
            DISTINCT(item_code) AS itm_code,
            item_name
        FROM purchased_raw_materials
    )
    
    SELECT 
        item_code, 
        item_name,
        uom,
        MAX(rate) AS rate,
        SUM(qty) AS total_quantity_purchased
    FROM purchased_raw_materials
    GROUP BY 1,2
    
    
    
