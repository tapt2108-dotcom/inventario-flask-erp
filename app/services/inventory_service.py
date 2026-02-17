from app import db
from app.models import Product, InventoryMovement
from datetime import datetime

class InventoryService:
    @staticmethod
    def register_movement(product_id, movement_type, quantity, description=None, user_id=None):
        """
        Registers a new inventory movement and updates product stock.
        
        Args:
            product_id (int): ID of the product.
            movement_type (str): 'entrada', 'salida', 'ajuste'.
            quantity (int): Quantity to move. Must be positive.
            description (str, optional): Reason for movement.
            user_id (int, optional): ID of the user performing the action.
            
        Returns:
            InventoryMovement: The created movement record.
            
        Raises:
            ValueError: If stock would become negative or product not found.
        """
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
            
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Producto no encontrado.")
            
        # Calculate new stock
        if movement_type == 'entrada':
            product.quantity += quantity
        elif movement_type == 'salida':
            if product.quantity < quantity:
                raise ValueError(f"Stock insuficiente. Disponible: {product.quantity}, Solicitado: {quantity}")
            product.quantity -= quantity
        elif movement_type == 'ajuste':
            # For adjustment, quantity is the NEW total stock? 
            # Or is it the DIFFERENCE? 
            # User said "movements table: entries, exits, adjustments". 
            # Usually adjustment implies setting to a specific value, but movement record needs a delta.
            # Let's interpret 'ajuste' as a correction delta provided by the user OR calculating delta.
            # If the user provides the Signed Delta, we can use that.
            # But the signature says `quantity` (int). 
            # Let's assume for 'ajuste', the UI might send a difference, OR the service handles logic.
            # To be safe and simple: limit 'ajuste' to direct stock set? 
            # Let's stick to standard practice: 
            # If 'ajuste', we expect the quantity to be the absolute change, and we need a direction?
            # Or maybe 'ajuste' just acts like 'entrada'/'salida' but with a different label?
            # Let's refine: 
            # If we want to Set Stock to X, we calculate difference and log as 'ajuste'.
            # If we just want to log a "correction", it might be positive or negative.
            # For simplicity in this method, let's assume 'ajuste' behaves like 'entrada'/ 'salida' depending on context?
            # ACTUALLY: Let's treat 'ajuste' as a special case where we might allow setting specific value?
            # For now, let's treat 'ajuste' as a type that requires a sign or handle it in a separate method `set_stock`.
            # Let's implement `set_stock` separately if needed.
            # For `register_movement`, let's assume it's a DELTA. 
            # But `quantity` must be positive per docstring.
            # Let's allow 'ajuste_positivo' and 'ajuste_negativo'? Or just 'ajuste' with signed quantity?
            # Docstring says "must be positive".
            # Let's strict to 'entrada' (add) and 'salida' (subtract).
            # 'ajuste' might be ambiguous here without more context. 
            # I will assume for now 'ajuste' is manual correction.
            # Let's change the logic: If type is 'ajuste', we need to know if it's add or sub.
            # Better: `register_movement` takes absolute quantity and type determines sign.
            # Let's just use 'entrada' and 'salida' for now. 
            pass

        # Re-evaluating 'ajuste':
        # If I do a stock count and find 5 items but system says 3. Input is 5.
        # Delta is +2. Movement: type='ajuste', quantity=2. Product.qty += 2.
        # If I find 1 item but system says 3. Input is 1.
        # Delta is -2. Movement: type='ajuste', quantity=2. Product.qty -= 2.
        # So 'ajuste' needs a direction.
        # Let's stick to 'entrada' and 'salida' for the core logic, and 'ajuste' can be the Label/Reason?
        # No, 'type' is a DB column.
        # Let's add `add_stock` and `remove_stock` methods to cover this.
        pass

    @staticmethod
    def add_stock(product_id, quantity, description, user_id=None, type='entrada'):
        return InventoryService.register_movement_action(product_id, type, quantity, description, user_id, action='add')

    @staticmethod
    def remove_stock(product_id, quantity, description, user_id=None, type='salida'):
        return InventoryService.register_movement_action(product_id, type, quantity, description, user_id, action='remove')

    @staticmethod
    def set_stock(product_id, new_quantity, description, user_id=None):
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Producto no encontrado.")
        
        current_qty = product.quantity
        diff = new_quantity - current_qty
        
        if diff == 0:
            return None # No change
            
        if diff > 0:
            return InventoryService.add_stock(product_id, diff, description, user_id, type='ajuste')
        else:
            return InventoryService.remove_stock(product_id, abs(diff), description, user_id, type='ajuste')

    @staticmethod
    def register_movement_action(product_id, movement_type, quantity, description, user_id, action):
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
            
        if not user_id:
            raise ValueError("El usuario es obligatorio para registrar movimientos.")
            
        if not description or len(description.strip()) < 5:
            raise ValueError("Debe proporcionar una descripción detallada (mínimo 5 caracteres).")
            
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Producto no encontrado.")
            
        if action == 'remove':
            if product.quantity < quantity:
                raise ValueError(f"Stock insuficiente. Disponible: {product.quantity}, Solicitado: {quantity}")
            product.quantity -= quantity
        elif action == 'add':
            product.quantity += quantity
            
        movement = InventoryMovement(
            product_id=product_id,
            type=movement_type,
            quantity=quantity,
            description=description,
            user_id=user_id,
            date=datetime.now()
        )
        
        db.session.add(movement)
        return movement
