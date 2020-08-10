import pandas as pd
from ortools.linear_solver import pywraplp


#task A
supplier_stock = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Supplier stock", index_col=0,
                                  header = 0)
raw_material_costs = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Raw material costs", index_col=0,
                                  header = 0)
raw_material_shipping = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Raw material shipping", index_col=0,
                                  header = 0)
product_requirements = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Product requirements", index_col=0,
                                  header = 0)
production_capacity = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Production capacity", index_col=0,
                                  header = 0)
production_cost = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Production cost", index_col=0,
                                  header = 0)
customer_demand = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Customer demand", index_col=0,
                                  header = 0)
shipping_costs = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = "Shipping costs", index_col=0,
                                  header = 0)

supplier_stock.fillna(0,inplace =True)
product_requirements.fillna(0,inplace =True)
production_capacity.fillna(0,inplace =True)
customer_demand.fillna(0,inplace =True)


suppliers = set(supplier_stock.index)
materials = set(supplier_stock.columns)
factories = set(raw_material_shipping.columns)
products = set(product_requirements.index)
customers = set(customer_demand.columns)

#task B : create decision variables
solver = pywraplp.Solver('LPWrapper', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

supplier_orders = {}
for factory in factories:
    for supplier in suppliers:
        for material in materials:
            if supplier_stock[material][supplier] > 0:
                supplier_orders[(factory, supplier, material)] = solver.IntVar(0, solver.infinity(), str((factory, supplier,material)))

production_volume = {}
for factory in factories:
    for product in products:
        if production_capacity[factory][product] > 0 :
            production_volume[(factory,product)] = solver.IntVar(0, solver.infinity(), str((factory,product)))

customer_delivery = {}
for factory in factories:
    for customer in customers:
        for product in products:
            if customer_demand[customer][product] > 0 and production_capacity[factory][product] >0:
                customer_delivery[(factory, customer, product)] = solver.IntVar(0, solver.infinity(), str((factory, customer, product)))

#task C : factories produce more than they ship to customers
for factory in factories:
    for product in products:
        constraint1 = solver.Constraint(0, solver.infinity())
        if (factory, product) in production_volume:
            constraint1.SetCoefficient(production_volume[( factory, product)],1 )
        for customer in customers:
            if (factory,customer,product) in customer_delivery:
                constraint1.SetCoefficient(customer_delivery[(factory, customer, product)],-1 )

#
#task D : customer demand is met
for customer in customers:
    for product in products:
        if customer_demand[customer][product] > 0:
            constraint2 = solver.Constraint(customer_demand[customer][product], customer_demand[customer][product])
            for factory in factories:
                if production_capacity[factory][product] > 0:
                    constraint2.SetCoefficient(customer_delivery[(factory, customer, product)],1)
# #
#task E : suppliers have all ordered items in stock
for supplier in suppliers:
    for material in materials:
        if supplier_stock[material][supplier] > 0:
            constraint3 = solver.Constraint(0, supplier_stock[material][supplier])
            for factory in factories:
                constraint3.SetCoefficient(supplier_orders[(factory, supplier, material)],1)
#
#task F : factories order enough material to be able to manufacture all items
for factory in factories:
    for material in materials:
        constraint4 = solver.Constraint(0, 0)
        for supplier in suppliers:
            if supplier_stock[material][supplier] > 0:
                constraint4.SetCoefficient(supplier_orders[(factory, supplier, material)],1)
        for product in products:
            if (factory,product) in production_volume and product_requirements[material][product] > 0:
                constraint4.SetCoefficient(production_volume[(factory, product)], -(product_requirements[material][product]))

#
# #task G : the manufacturing capacities are not exceeded
for factory in factories:
    for product in products:
        if production_capacity[factory][product] > 0:
            constraint5 = solver.Constraint(0,production_capacity[factory][product])
            constraint5.SetCoefficient(production_volume[(factory, product)],1)

#task H :objective function
cost = solver.Objective()
for factory in factories:
    for supplier in suppliers:
        for material in materials:
            if supplier_stock[material][supplier] > 0:
                cost.SetCoefficient(supplier_orders[(factory, supplier, material)],raw_material_costs[material][supplier]
                                + raw_material_shipping[factory][supplier])
    for product in products:
        if (factory,product) in production_volume:
            cost.SetCoefficient(production_volume[(factory, product)],production_cost[factory][product])
        for customer in customers:
            if (factory, customer, product) in customer_delivery:
                cost.SetCoefficient(customer_delivery[(factory, customer, product)],int(shipping_costs[customer][factory]))

cost.SetMinimization()
solver.Solve()

#task I: determine optimal overall cost
print("Optimal Overall Cost : ",cost.Value())
print()

#task J : determine how much material each factory should order from the suppliers.
print("How many units of each material does each factory order from each supplier?")
for factory in factories:
    print(factory," : ")
    for supplier in suppliers:
        for material in materials:
            if (factory, supplier, material) in supplier_orders \
                    and supplier_orders[(factory, supplier, material)].solution_value() > 0:
                print (supplier, " supplies ",supplier_orders[(factory, supplier, material)].solution_value() ," units of ",material)
print()

#task K : determine for each factory the bill inclusive of material and delivery cost from each supplier
print("What is the bill amount to be paid by each factory to each of its suppliers (inclusive of material cost and shipping)?")
for factory in factories:
    print(factory ," : ")
    for supplier in suppliers:
        c = 0
        for material in materials:
            if (factory, supplier, material) in supplier_orders \
                    and supplier_orders[(factory, supplier, material)].solution_value() > 0:
                c += raw_material_costs[material][supplier]+ raw_material_shipping[factory][supplier]
        print (supplier, " : ", c)
print()

#task L : determine for each factory how many units of each product are being manufactured. Also, determine total manufacturing cost for each individual factory.
print("How many units per product are manufactured in each factory? What is the total manufacturing cost of each factory?")
for factory in factories:
    print(factory," : ")
    mc = 0
    for product in products:
        if (factory, product) in production_volume \
            and production_volume[(factory,product)].solution_value() > 0:
            mc += production_cost[factory][product]
            print(product," : ", production_volume[(factory,product)].solution_value()," units")
    print("Total Manufacturing cost :",mc)
print()

#task M : determine for each customer how many units of each product are being shipped from each factory and also the total shipping cost per customer
print("How many units of each product are being shipped to each customer and from which factory? Also, what is the total shipping cost for each customer?")
for customer in customers:
    print(customer," : ")
    c = 0
    for factory in factories:
        for product in products:
            if customer_demand[customer][product] > 0 and production_capacity[factory][product] >0 \
                and customer_delivery[(factory, customer, product)].solution_value() > 0:
                print(customer_delivery[(factory, customer, product)].solution_value(), " units of ",product," from ",factory)
                c += shipping_costs[customer][factory]
    print("Total Shipping cost : ",c)
print()

# task N : Determine for each customer the fraction of each material each factory has to order
# for manufacturing products delivered to that particular customer. Based on
# this calculate the overall unit cost of each product per customer including the raw
# materials used for the manufacturing of the customer’s specific product, the cost of
# manufacturing for the specific customer and all relevant shipping costs.
total_cost = 0
material_fraction_d= {}
for customer in customers:
    print(customer , " : ")
    for product in products:
        if customer_demand[customer][product] > 0:
            print(product, " : ")
            for factory in factories:
                if production_capacity[factory][product] > 0 and production_volume[(factory,product)].solution_value() > 0:
                    if customer_demand[customer][product] > 0 and production_capacity[factory][product] >0 \
                                and customer_delivery[(factory, customer, product)].solution_value() > 0:
                        for material in materials:
                            for supplier in suppliers:
                                if supplier_stock[material][supplier] > 0 and supplier_orders[(factory, supplier, material)].solution_value() >0 \
                                    and product_requirements[material][product] > 0:
                                    material_fraction = supplier_orders[(factory, supplier, material)].solution_value()/(customer_delivery[(factory, customer, product)].solution_value()
                                            *product_requirements[material][product])
                                    print(factory," ", material," ", supplier," ",material_fraction)
                                    material_fraction_d[(customer,product,factory, supplier, material)] = material_fraction
    print()

print("Per customer per product cost:")
print(material_fraction_d)
for customer in customers:
    for product in products:
        c = 0
        for factory in factories:
            for supplier in suppliers:
                for material in materials:
                    if (customer,product,factory, supplier, material) in material_fraction_d.keys():
                        c += (raw_material_costs[material][supplier] + raw_material_shipping[factory][supplier]) \
                             * material_fraction_d[(customer,product,factory, supplier, material)]
                        print(c)

        if c>0:
            c += production_cost[factory][product] + shipping_costs[customer][factory]
            print(customer, " ", product, " ", c)



