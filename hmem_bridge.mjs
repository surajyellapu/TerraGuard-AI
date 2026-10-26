import path from "node:path";
import { HMEM } from "./engines/hmem/reference/src/index.ts";

const memoryDirectory = path.resolve(".terraguard_hmem");

const hmem = new HMEM({
  actor: "TerraGuard",
  persistDir: memoryDirectory,
});

function addEvidence(content, source) {
  if (!content || !content.trim()) {
    throw new Error("Evidence content is required.");
  }

  if (!source || !source.trim()) {
    throw new Error("Evidence source is required.");
  }

  return hmem.add({
    content: content,
    type: "factual",
    layer: "working",
    source: source,
    confidence: 0.7,
    tags: ["terraguard", "simulated-evidence"],
  });
}
function addStructuredEvidence(evidence) {
  if (!evidence || typeof evidence !== "object" || Array.isArray(evidence)) {
    throw new Error("Evidence must be a JSON object.");
  }

  if (!evidence.id || !evidence.claim || !evidence.source) {
    throw new Error("Evidence must include id, claim, and source.");
  }

  const content = JSON.stringify({
    ...evidence,
    data_notice: "Sample evidence; not independently verified.",
  });

  return hmem.add({
    content,
    type: "factual",
    layer: "working",
    source: String(evidence.source),
    confidence: 0.7,
    tags: [
      "terraguard",
      "simulated-evidence",
      `observation:${String(evidence.id)}`,
      `status:${String(evidence.status || "unknown")}`,
    ],
    provenance: {
      origin: "manual",
      learnedAt: Date.now(),
      label: `TerraGuard sample observation ${String(evidence.id)}`,
      refs: [String(evidence.id)],
    },
  });
}
function searchEvidence(query) {
  if (!query || !query.trim()) {
    throw new Error("Search query is required.");
  }

  return hmem.query(query, {
    threshold: 0.3,
    topN: 5,
  });
}

async function main() {
  const [operation, ...args] = process.argv.slice(2);
  if (operation === "add-json") {
    const evidence = JSON.parse(args[0] || "{}");
    const record = await addStructuredEvidence(evidence);

    console.log(JSON.stringify({
      success: true,
      memoryId: record.id,
      observationId: evidence.id,
      source: record.source,
      content: record.content,
      notice: "Stored sample evidence; not independently verified.",
    }, null, 2));

    return;
  }
  if (operation === "add") {
    const content = args[0] || "";
    const source = args[1] || "";

    const record = await addEvidence(content, source);

    console.log(JSON.stringify({
      success: true,
      memoryId: record.id,
      source: record.source,
      content: record.content,
      notice: "Stored note; not verified real-world evidence.",
    }, null, 2));

    return;
  }

  if (operation === "search") {
    const query = args.join(" ");
    const result = await searchEvidence(query);

    console.log(JSON.stringify({
      success: true,
      query: query,
      memories: result.memories.map((item) => ({
        id: item.memory.id,
        content: item.memory.content,
        source: item.memory.source,
        confidence: item.memory.confidence,
        relevance: item.relevance,
      })),
      notice: "Retrieved notes do not confirm a flood.",
    }, null, 2));

    return;
  }

  console.error(
    'Usage: add "<note>" "<source>" OR search "<query>"'
  );
  process.exitCode = 2;
}

main().catch((error) => {
  console.error(
    error instanceof Error ? error.message : "Unexpected bridge error"
  );
  process.exitCode = 1;
});