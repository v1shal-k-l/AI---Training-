from tools import (
    search_products,
    calculate_order_total
)


class InventoryAgent:

    async def run(self, context):

        print(
            "\n========== INVENTORY AGENT =========="
        )

        category = context["category"]

        result = search_products(
            category
        )

        if not result["success"]:

            print(
                "\n🤖 Inventory Agent:"
            )

            print(
                result["message"]
            )

            context["inventory_result"] = result

            return context

        print(
            "\n🤖 Inventory Agent:"
        )

        print(
            f"Found {len(result['products'])} matching products."
        )

        for product in result["products"]:

            print(
                f"""
Product ID : {product['id']}
Name       : {product['name']}
Price      : ₹{product['price_inr']:,}
Stock      : {product['stock']}
Rating     : {product['rating']}⭐
"""
            )

        context["inventory_result"] = result

        return context


class PricingAgent:

    async def run(self, context):

        print(
            "\n========== PRICING AGENT =========="
        )

        inventory = context["inventory_result"]

        quantity = context["quantity"]

        budget = context["budget"]

        affordable_products = []

        if not inventory["success"]:

            context["pricing_result"] = []

            return context

        for product in inventory["products"]:

            price_result = calculate_order_total(
                product["id"],
                quantity
            )

            if not price_result["success"]:
                continue

            print(
                f"""
Product : {price_result['product_name']}
Quantity: {quantity}
Cost    : ₹{price_result['total_cost']:,}
Budget  : ₹{budget:,}
"""
            )

            if (
                price_result["total_cost"]
                <= budget
            ):
                affordable_products.append(
                    price_result
                )

        if affordable_products:

            print(
                "\n✅ Affordable products identified."
            )

        else:

            print(
                "\n⚠️ No products found within budget."
            )

        context["pricing_result"] = (
            affordable_products
        )

        return context


class RecommendationAgent:

    async def run(self, context):

        print(
            "\n========== RECOMMENDATION AGENT =========="
        )

        products = context["pricing_result"]

        if not products:

            context["recommendation"] = """
🤖 Shopping Assistant:

I couldn't find any products that satisfy your quantity and budget requirements.

You may try:

• Increasing the budget
• Reducing the quantity
• Selecting another category

Would you like me to search again with different criteria?
"""

            return context

        # Highest rating first
        # If tie → lowest cost

        best_product = sorted(

            products,

            key=lambda item: (
                -item["rating"],
                item["total_cost"]
            )

        )[0]

        recommendation = f"""
🤖 Shopping Assistant:

I recommend **{best_product['product_name']}**.

📦 Product ID: {best_product['product_id']}
🛒 Quantity: {best_product['quantity']}
💰 Total Cost: ₹{best_product['total_cost']:,}
⭐ Customer Rating: {best_product['rating']}

Why this recommendation?

✅ Available in stock
✅ Within your budget
✅ Highest-rated among affordable options

Would you like me to show alternative products as well?
"""

        print(
            "\n✅ Best product selected."
        )

        context["recommendation"] = (
            recommendation
        )

        return context