const { GoogleGenerativeAI } = require("@google/generative-ai");

// Initialize Google AI
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-pro" });

exports.handler = async function(event, context) {
  try {
    const path = event.path.split('/').pop();
    const body = JSON.parse(event.body || '{}');

    switch (path) {
      case 'process':
        const processResult = await processIdea(body.idea);
        return {
          statusCode: 200,
          body: JSON.stringify(processResult)
        };

      case 'refine':
        const refineResult = await refineContent(body.refinement);
        return {
          statusCode: 200,
          body: JSON.stringify(refineResult)
        };

      case 'finalize':
        const blogResult = await finalizeToBlog();
        return {
          statusCode: 200,
          body: JSON.stringify({ blog_post: blogResult })
        };

      default:
        return {
          statusCode: 404,
          body: JSON.stringify({ error: 'Not Found' })
        };
    }
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
}

async function processIdea(idea) {
  const prompt = `Process this idea: ${idea}`;
  const result = await model.generateContent(prompt);
  const text = result.response.text();
  
  return parseResponse(text);
}

async function refineContent(refinement) {
  const prompt = `Refine this content: ${refinement}`;
  const result = await model.generateContent(prompt);
  const text = result.response.text();
  
  return parseResponse(text);
}

async function finalizeToBlog() {
  const prompt = "Convert the current content to a blog post";
  const result = await model.generateContent(prompt);
  return result.response.text();
}

function parseResponse(text) {
  // Extract content from XML-like tags
  const connected = text.match(/<connected_narrative>(.*?)<\/connected_narrative>/s)?.[1] || '';
  const growth = text.match(/<growth_points>(.*?)<\/growth_points>/s)?.[1] || '';
  const contributions = text.match(/<ai_contributions>(.*?)<\/ai_contributions>/s)?.[1] || '';

  return {
    connected_narrative: connected.trim(),
    growth_points: growth.trim(),
    ai_contributions: contributions.trim()
  };
}