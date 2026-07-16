import { Box, Chip, Stack, Typography } from "@mui/material";

import type { PurchaseListItem } from "../api/purchaseListApi";
import {
  formatPackageCount,
  formatPurchaseQuantity,
  purchaseListResponsiveDirection,
} from "../model/purchaseListState";

export default function PurchaseListItemRow({ item }: { item: PurchaseListItem }) {
  const hasSurplus = item.surplus_quantity > 0;

  return (
    <Box sx={{ py: 1.5 }}>
      <Stack spacing={1}>
        <Stack
          direction={purchaseListResponsiveDirection}
          spacing={1}
          justifyContent="space-between"
          alignItems={{ xs: "flex-start", sm: "center" }}
        >
          <Typography fontWeight={600}>{item.product_name}</Typography>
          <Chip
            size="small"
            color={hasSurplus ? "warning" : "success"}
            label={
              hasSurplus
                ? `Излишек ${formatPurchaseQuantity(
                    item.surplus_quantity,
                    item.package_unit,
                  )}`
                : "Без излишка"
            }
          />
        </Stack>

        <Stack direction={purchaseListResponsiveDirection} spacing={2} flexWrap="wrap">
          <Typography variant="body2">
            Требуется: {formatPurchaseQuantity(item.required_quantity, item.required_unit)}
          </Typography>
          <Typography variant="body2">
            Фасовка: {formatPurchaseQuantity(item.package_size, item.package_unit)} ×{" "}
            {formatPackageCount(item.packages_count)}
          </Typography>
          <Typography variant="body2" fontWeight={600}>
            Купить: {formatPurchaseQuantity(item.purchase_quantity, item.package_unit)}
          </Typography>
        </Stack>
      </Stack>
    </Box>
  );
}
