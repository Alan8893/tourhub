import { Box, Paper, Stack, Typography } from "@mui/material";

import type {
  DocumentAppearanceDraft,
  DocumentLogoSource,
} from "../api/documentAppearanceSettingsApi";
import type { ClubSettingsDetail } from "../api/systemSettingsApi";

const LOGO_KEYS: Record<Exclude<DocumentLogoSource, "none">, keyof ClubSettingsDetail["images"]> = {
  main_logo: "main_logo_data_url",
  document_image: "document_image_data_url",
  light_logo: "light_logo_data_url",
  dark_logo: "dark_logo_data_url",
};

function selectedLogo(
  source: DocumentLogoSource,
  club: ClubSettingsDetail,
): string | null {
  if (source === "none") return null;
  return club.images[LOGO_KEYS[source]] ?? club.images.main_logo_data_url;
}

function contactLines(club: ClubSettingsDetail): string[] {
  return [
    [club.city, club.region].filter(Boolean).join(", "),
    club.address,
    club.phone ? `Тел.: ${club.phone}` : null,
    club.email ? `Email: ${club.email}` : null,
    club.website,
  ].filter((value): value is string => Boolean(value));
}

interface DocumentAppearancePreviewProps {
  draft: DocumentAppearanceDraft;
  club: ClubSettingsDetail;
}

export default function DocumentAppearancePreview({
  draft,
  club,
}: DocumentAppearancePreviewProps) {
  const logo = selectedLogo(draft.logo_source, club);
  const contacts = draft.show_contacts ? contactLines(club) : [];
  const compact = draft.table_density === "compact";
  const titleBackground =
    draft.use_document_image_as_title_background && club.images.document_image_data_url;

  return (
    <Paper
      variant="outlined"
      sx={{
        mx: "auto",
        width: "100%",
        maxWidth: 760,
        minWidth: 0,
        overflow: "hidden",
        bgcolor: "common.white",
        color: "common.black",
      }}
      aria-label="Предпросмотр документа"
    >
      <Box
        sx={{
          position: "relative",
          minWidth: 0,
          minHeight: titleBackground ? 120 : 64,
          p: 2,
          bgcolor: draft.title_background_color,
          overflow: "hidden",
        }}
      >
        {titleBackground && (
          <Box
            component="img"
            src={titleBackground}
            alt=""
            sx={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              objectFit: "cover",
              opacity: 0.28,
            }}
          />
        )}
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={2}
          alignItems={{ xs: "stretch", sm: "flex-start" }}
          sx={{ position: "relative", minWidth: 0 }}
        >
          {logo ? (
            <Box
              component="img"
              src={logo}
              alt="Выбранный логотип"
              sx={{ width: 72, maxHeight: 52, objectFit: "contain", flexShrink: 0 }}
            />
          ) : (
            <Box
              sx={{
                width: 72,
                height: 44,
                border: "1px dashed",
                borderColor: draft.table_border_color,
                display: "grid",
                placeItems: "center",
                fontSize: 11,
                flexShrink: 0,
              }}
            >
              Без логотипа
            </Box>
          )}
          <Box sx={{ minWidth: 0 }}>
            <Typography
              sx={{
                color: draft.heading_color,
                fontWeight: 800,
                fontSize: 20,
                overflowWrap: "anywhere",
              }}
            >
              {club.club_name}
            </Typography>
            {contacts.map((line) => (
              <Typography
                key={line}
                sx={{ fontSize: 11, lineHeight: 1.35, overflowWrap: "anywhere" }}
              >
                {line}
              </Typography>
            ))}
          </Box>
        </Stack>
      </Box>

      <Stack spacing={2} sx={{ p: { xs: 2, sm: 3 }, minWidth: 0 }}>
        <Box sx={{ minWidth: 0 }}>
          <Typography
            sx={{
              color: draft.heading_color,
              fontWeight: 800,
              fontSize: 24,
              overflowWrap: "anywhere",
            }}
          >
            Закупочный лист
          </Typography>
          <Typography sx={{ color: draft.primary_color, fontSize: 12 }}>
            Проект «Тестовый поход»
          </Typography>
        </Box>

        <Box sx={{ width: "100%", maxWidth: "100%", minWidth: 0, overflowX: "auto" }}>
          <Box
            component="table"
            sx={{ width: "100%", borderCollapse: "collapse", minWidth: 420 }}
          >
            <Box component="thead">
              <Box component="tr">
                {["Продукт", "Количество", "Единица", "Упаковок"].map((label) => (
                  <Box
                    component="th"
                    key={label}
                    sx={{
                      p: compact ? 0.75 : 1.25,
                      bgcolor: draft.table_header_background,
                      color: draft.table_header_text,
                      border: "1px solid",
                      borderColor: draft.table_border_color,
                      textAlign: "left",
                      fontSize: 12,
                    }}
                  >
                    {label}
                  </Box>
                ))}
              </Box>
            </Box>
            <Box component="tbody">
              {[
                ["Гречка", "2", "кг", "4"],
                ["Чай", "0,5", "кг", "2"],
              ].map((row) => (
                <Box component="tr" key={row[0]}>
                  {row.map((value) => (
                    <Box
                      component="td"
                      key={value}
                      sx={{
                        p: compact ? 0.75 : 1.25,
                        border: "1px solid",
                        borderColor: draft.table_border_color,
                        fontSize: 12,
                      }}
                    >
                      {value}
                    </Box>
                  ))}
                </Box>
              ))}
            </Box>
          </Box>
        </Box>

        <Box
          sx={{
            minWidth: 0,
            borderTop: "2px solid",
            borderColor: draft.accent_color,
            pt: 1,
            color: draft.primary_color,
            fontSize: 11,
            overflowWrap: "anywhere",
          }}
        >
          {draft.footer_text || `Сформировано для ${club.club_name} в TourHub`}
        </Box>
      </Stack>
    </Paper>
  );
}
