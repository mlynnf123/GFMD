# GFMD Documents Directory

This directory contains the knowledge base documents for your GFMD Swarm Agent system.

## File Structure

Add your company documents here in `.txt` or `.md` format:

### Company Information
- `company_overview.txt` - Company background, history, mission
- `services_description.txt` - Core services and offerings  
- `capabilities.txt` - Technical capabilities and differentiators
- `product_catalog.txt` - Product lines and specifications

### Sales Materials
- `value_proposition.txt` - Key value propositions for different markets
- `sales_playbook.txt` - Sales strategies and approaches
- `case_studies.txt` - Customer success stories and testimonials
- `competitive_advantages.txt` - How you differentiate from competitors
- `pricing_structure.txt` - Pricing models and packages

### Industry-Specific Content
- `healthcare_solutions.txt` - Healthcare-specific offerings
- `restaurant_solutions.txt` - Restaurant industry solutions
- `education_solutions.txt` - Educational institution offerings
- `retail_solutions.txt` - Retail market solutions

## Adding Documents

1. **Create text files** with your actual company content
2. **Use descriptive filenames** that match your content type
3. **Restart your vector system** to load new documents
4. **Test searches** to ensure content is properly indexed

## Content Guidelines

- **Be specific**: Include actual product names, specifications, and capabilities
- **Include numbers**: Metrics, case study results, pricing information
- **Use keywords**: Terms your prospects would search for
- **Keep current**: Update documents regularly as offerings change

## Loading Process

The system will automatically:
1. Scan this directory for `.txt` and `.md` files
2. Split large documents into searchable chunks
3. Create embeddings using Vertex AI
4. Store in the vector database for agent access

Files are loaded when you call:
```python
loader.load_company_info()
loader.load_sales_materials()
```

Or individually:
```python
loader.load_from_file('path/to/document.txt', 'document_type')
```