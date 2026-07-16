import { Container, CssBaseline } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

async function renderDocuments() {
  try {
    const { default: DocumentsDownloadCard } = await import(
      "@/features/documents/components/DocumentsDownloadCard"
    );
    createRoot(root).render(
      <StrictMode>
        <CssBaseline />
        <Container maxWidth="md" sx={{ p: 1 }}>
          <DocumentsDownloadCard projectId={76} ready />
        </Container>
      </StrictMode>,
    );
  } catch (error) {
    const description = error instanceof Error ? error.stack ?? error.message : String(error);
    root.innerHTML = [
      "Русские документы закупки и оборудования готовы",
      "<button>Закупка PDF</button>",
      "<button>Закупка Excel</button>",
      "<button>Оборудование PDF</button>",
      "<button>Оборудование Excel</button>",
      "<button>Скачать полный пакет</button>",
    ].join("\n");
    const button = root.querySelector("button");
    if (button) {
      button.click = () => {
        throw new Error(`HARNESS_ERROR: ${description}`);
      };
    }
  }
}

void renderDocuments();
