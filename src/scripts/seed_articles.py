#!/usr/bin/env python
"""
Django management script to seed the database with article tags and articles.
This script creates the three main tags (diabetes, malaria, research) and populates
the database with articles based on the content from the text file.
"""

import os
import sys
import django
from datetime import date, datetime
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import ArticleTag, Article, ResearchPaper
from django.core.files.base import ContentFile

def create_tags():
    """Create the three main article tags"""
    tags_data = [
        {
            'name': 'diabetes',
            'description': 'Articles and research related to diabetes mellitus, including epidemiology, treatment, and prevention strategies.',
            'color': '#dc3545',
            'icon': 'fas fa-syringe'
        },
        {
            'name': 'malaria',
            'description': 'Articles and research related to malaria, including epidemiology, diagnosis, treatment, and control strategies.',
            'color': '#28a745',
            'icon': 'fas fa-bug'
        },
        {
            'name': 'research',
            'description': 'Research papers and scientific studies related to various diseases and health conditions.',
            'color': '#007bff',
            'icon': 'fas fa-microscope'
        }
    ]
    
    created_tags = {}
    for tag_data in tags_data:
        tag, created = ArticleTag.objects.get_or_create(
            name=tag_data['name'],
            defaults=tag_data
        )
        created_tags[tag.name] = tag
        if created:
            print(f"✓ Created tag: {tag.name}")
        else:
            print(f"✓ Tag already exists: {tag.name}")
    
    return created_tags

def create_malaria_articles(tags):
    """Create malaria-related articles"""
    malaria_tag = tags['malaria']
    research_tag = tags['research']
    
    malaria_articles = [
        {
            'title': 'Current Status of Malaria Control and Elimination in Africa: Epidemiology, Diagnosis, Treatment, Progress and Challenges',
            'summary': 'A comprehensive review article discussing the current status, challenges, and progress of malaria control and elimination efforts in Africa, highlighting epidemiological data, treatment strategies, and the impact of various factors on malaria transmission.',
            'content': '''
# Current Status of Malaria Control and Elimination in Africa

## Overview
This review discusses the epidemiology, diagnosis, treatment, progress, and challenges of malaria control and elimination in Africa. Africa bears the highest malaria burden globally, with P. falciparum being the leading cause of death.

## Key Findings

### Epidemiological Characteristics
- In 2022, there were approximately 249 million malaria cases worldwide, with 94% (233 million) in Africa
- Nigeria, the Democratic Republic of the Congo, Uganda, and Mozambique accounted for nearly half of global cases
- Malaria incidence in the WHO African Region decreased from 370 to 223 per 1,000 population from 2000 to 2022
- Africa accounts for about 95% of global malaria deaths, with Nigeria alone contributing 31%

### Species and Distribution
Five species cause malaria in humans: P. falciparum, P. malariae, P. vivax, P. ovale, and P. knowlesi. P. falciparum is responsible for over 90% of malaria deaths globally.

### Susceptible Populations
- Infants, young children, and pregnant women are most susceptible due to low immunity
- Pregnant women are three times more likely to contract malaria compared to non-pregnant women
- HIV-infected individuals face worse prognoses when co-infected with malaria

### Challenges
- Climate change and environmental destruction
- Poverty and inadequate health services
- Drug resistance to antimalarial medications
- Insecticide resistance in mosquito vectors
- Cross-border transmission

### Progress Made
- Between 2000 and 2022, malaria incidence decreased by 40% and mortality by 60% in the WHO African Region
- International funding for malaria control has increased nearly 20 times since 2000
- The mortality rate from falciparum malaria has halved from 2000 to 2022

### Strategies for Improvement
- Joint prevention and treatment approaches
- Development of new antimalarial drugs
- Vaccination efforts (RTS,S/AS01 and R21/Matrix-M vaccines)
- Enhanced surveillance and monitoring systems
- Community education and awareness programs
            ''',
            'article_type': 'research',
            'author_name': 'Research Team',
            'author_credentials': 'Public Health Researchers',
            'author_affiliation': 'African Health Research Institute',
            'publication_date': date(2024, 1, 15),
            'estimated_read_time': 12,
            'reference_link': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11442732/',
            'tags': [malaria_tag, research_tag],
            'is_featured': True
        },
        {
            'title': 'GUIDELINES FOR CASE MANAGEMENT OF MALARIA',
            'summary': 'Comprehensive guidelines for the case management of malaria in Ghana, including diagnosis, treatment protocols, and prevention strategies.',
            'content': '''
# Guidelines for Malaria Case Management in Ghana

## Overview
These guidelines provide standardized recommendations for the management of malaria in Ghana, replacing the previous 2009 guidelines. They were developed through consultative meetings involving the Ministry of Health, Ghana Health Service, WHO, and other partners.

## Key Components

### Malaria Overview in Ghana
- Malaria is a significant health issue in Ghana, particularly affecting children and pregnant women
- Caused by Plasmodium parasites, primarily P. falciparum (80-90%)
- Major vectors include Anopheles gambiae and Anopheles funestus
- In 2012, malaria accounted for 38.9% of outpatient illnesses and 38.8% of admissions

### Treatment Protocol for Uncomplicated Malaria
- Artemisinin-based Combination Therapy (ACT) is the national policy for treatment since 2004
- Recommended ACTs include Artesunate-Amodiaquine, Artemether-Lumefantrine, and Dihydroartemisinin-Piperaquine
- Treatment should be supervised, especially for children

### Management of Severe Malaria
- Severe malaria is a medical emergency requiring immediate intervention
- Common complications include cerebral malaria, severe anemia, and hypoglycemia
- Initial treatment should start with parenteral anti-malarial medications like IV/IM Artesunate or Quinine

### Preventive Measures
- Use of insecticide-treated nets (ITNs)
- Indoor residual spraying (IRS)
- Seasonal malaria chemoprevention (SMC) for children aged 3-59 months
- Intermittent preventive treatment (IPTp) for pregnant women

### Diagnosis
- Microscopic detection of blood smears is the gold standard
- Rapid diagnostic tests (RDTs) offer quick results
- PCR can detect Plasmodium DNA and identify drug resistance
            ''',
            'article_type': 'guideline',
            'author_name': 'Ghana Health Service',
            'author_credentials': 'Ministry of Health',
            'author_affiliation': 'Ghana Health Service',
            'publication_date': date(2024, 2, 1),
            'estimated_read_time': 8,
            'reference_link': 'https://www.severemalaria.org/countries/ghana',
            'tags': [malaria_tag],
            'is_featured': False
        },
        {
            'title': 'Distribution and Risk Factors of Malaria in the Greater Accra Region in Ghana',
            'summary': 'A study on the distribution and risk factors of malaria in the Greater Accra Region of Ghana, analyzing spatial and temporal patterns to inform targeted health resource allocation.',
            'content': '''
# Distribution and Risk Factors of Malaria in Greater Accra Region

## Study Overview
This study investigates the spatial, temporal, and spatio-temporal patterns of malaria in the Greater Accra Region of Ghana to inform targeted health resource allocation.

## Key Findings

### Epidemiological Data
- A total of 1,105,370 malaria cases were reported from 2015 to 2019
- Significant seasonal variation was observed, with peaks in June and July
- The annual parasite index (API) varied between 4 and 185 across districts

### Hotspot Districts
- Kpone-Katamanso
- Ashaiman
- Tema
- La-Nkwantanang-Madina

### Risk Factors
- Monthly rainfall (AOR = 1.01)
- Previous month's cases (AOR = 1.064)
- Minimum temperature (AOR = 0.86) - negative correlation
- Population density (AOR = 0.996) - negative correlation

### Spatial Analysis
- Global Moran's I statistic indicated clustering effect (I = 0.111, p < 0.001)
- Eight space-time clusters were identified
- Primary cluster occurred from February 2015 to July 2017 with relative risk of 4.66

### Policy Implications
- Targeted interventions necessary in hotspot districts
- Control measures should be prioritized during peak months (June and July)
- Findings can guide national malaria programs in resource allocation
            ''',
            'article_type': 'research',
            'author_name': 'K.K., E.D., A.L., M.K., K.W.',
            'author_credentials': 'Public Health Researchers',
            'author_affiliation': 'Australian National University & Ghana Health Service',
            'publication_date': date(2024, 3, 1),
            'estimated_read_time': 10,
            'reference_link': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC9566805/',
            'tags': [malaria_tag, research_tag],
            'is_featured': True
        }
    ]
    
    created_articles = []
    for article_data in malaria_articles:
        tags = article_data.pop('tags')
        article = Article.objects.create(**article_data)
        article.tags.set(tags)
        created_articles.append(article)
        print(f"✓ Created malaria article: {article.title}")
    
    return created_articles

def create_diabetes_articles(tags):
    """Create diabetes-related articles"""
    diabetes_tag = tags['diabetes']
    research_tag = tags['research']
    
    diabetes_articles = [
        {
            'title': 'The Epidemiological and Economic Burden of Diabetes in Ghana: A Scoping Review to Inform Health Technology Assessment',
            'summary': 'A scoping review evaluating the epidemiological and economic burden of diabetes in Ghana to inform Health Technology Assessment (HTA) and national policy.',
            'content': '''
# The Epidemiological and Economic Burden of Diabetes in Ghana

## Executive Summary
This scoping review evaluates the epidemiological and economic burden of diabetes in Ghana to inform Health Technology Assessment (HTA) and national policy. It highlights significant regional disparities, gaps in economic data, and urgent needs for targeted interventions.

## Key Findings

### Epidemiological Burden
- **National Prevalence**: 2.80%–3.95% (higher in women and urban areas)
- **Regional Variations**:
  - Western Region: 39.80%
  - Ashanti Region: 25.20%
  - Central Region: 24.60%

### Risk Factors
- Urbanization and physical inactivity
- Dietary habits and processed food consumption
- Socioeconomic status and education level
- Age and gender disparities

### Health Outcomes
- **Complications**:
  - Metabolic Syndrome: Up to 90% in Ashanti Region
  - Hypertension: 36.6% prevalence in Greater Accra
  - Diabetic Foot Disorders: 8.39% incidence in Ashanti; 11% ulcer prevalence nationally

### Economic Burden
- **Annual Cost per Patient**: GHS 540.35 (US $194.09) for outpatient care
- Drugs account for 71% of direct medical costs
- Limited data on productivity loss, DALYs, or QALYs

### Policy Implications
- Targeted interventions for high-prevalence regions
- Strengthen HTA for cost-effective diabetes management
- Expand surveillance systems for economic impacts
- Address shared risk factors through lifestyle campaigns
            ''',
            'article_type': 'research',
            'author_name': 'Public Health Research Team',
            'author_credentials': 'Health Technology Assessment Specialists',
            'author_affiliation': 'Ghana Health Research Institute',
            'publication_date': date(2024, 1, 20),
            'estimated_read_time': 15,
            'reference_link': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10931482/',
            'tags': [diabetes_tag, research_tag],
            'is_featured': True
        },
        {
            'title': 'Cost of Diabetes Mellitus and Associated Factors – An Institutional Cross-Sectional Study in Ghana',
            'summary': 'A comprehensive study examining the cost burden of diabetes mellitus and associated factors in Ghana.',
            'content': '''
# Cost of Diabetes Mellitus and Associated Factors in Ghana

## Study Overview
This cross-sectional study examines the cost burden of diabetes mellitus and associated factors in Ghana, providing insights into both direct and indirect costs.

## Key Findings

### Economic Burden
- **Annual Cost per Patient**: $290.44
- **Direct Costs**: 54.99% (medications, consultations, transportation)
- **Indirect Costs**: 45.01% (lost wages due to illness/hospital visits)

### Cost Drivers
- **Medications**: Primary driver of direct costs
- **Complications**: Stroke (+126%) and retinopathy (+43%)
- **Duration**: Longer illness duration increases costs (+4% per year)
- **Gender**: Males incur higher costs (+42%)

### Regional Variations
- Urban areas show lower costs despite higher prevalence
- Rural residents face higher indirect costs (travel, lost wages)
- Better healthcare access in urban areas reduces overall burden

### Policy Recommendations
- Mitigate catastrophic expenditures via insurance schemes
- Expand rural healthcare access to reduce indirect costs
- Implement early detection programs for complications
- Develop targeted interventions for high-risk populations
            ''',
            'article_type': 'research',
            'author_name': 'Health Economics Research Team',
            'author_credentials': 'Health Economists',
            'author_affiliation': 'Tamale Teaching Hospital',
            'publication_date': date(2024, 2, 15),
            'estimated_read_time': 12,
            'reference_link': 'https://bmchealthservres.biomedcentral.com/articles/10.1186/s12913-025-12667-z',
            'tags': [diabetes_tag, research_tag],
            'is_featured': False
        },
        {
            'title': 'Prevalence Study of Type 2 Diabetes Mellitus in the Ashanti Region of Ghana: A Systematic Review of Risk Factors',
            'summary': 'A systematic review assessing the prevalence and key risk factors of type 2 diabetes mellitus among adults in the Ashanti Region of Ghana.',
            'content': '''
# Prevalence Study of Type 2 Diabetes Mellitus in the Ashanti Region

## Study Objective
This systematic review assesses the prevalence and key risk factors of type 2 diabetes mellitus (T2DM) among adults in the Ashanti Region of Ghana.

## Methodology
- Systematic review following PRISMA guidelines
- Literature search from January 2011 to December 2020
- 12 studies met inclusion criteria from 268 articles retrieved

## Key Findings

### Prevalence Patterns
- **Regional Prevalence**: 3.8% (higher than Ghana's national average of 2.5%)
- **Urban vs Rural**: Higher prevalence in urban areas
- **Gender**: Women more affected, especially with higher education

### Major Risk Factors
- **Physical Inactivity**: Sedentary jobs in urban areas
- **Obesity**: Linked to dietary habits and socioeconomic status
- **Lifestyle Behaviors**: Overeating, alcohol, smoking, processed foods
- **Dietary Patterns**: High consumption of sweets, rice, meat
- **Age**: Older adults more susceptible

### Cultural and Structural Factors
- Some communities associate diabetes with supernatural causes
- Urbanization compounds disease burden
- Inadequate access to health services in rural areas

### Healthcare Access
- Urban dwellers show higher adherence to diabetes management
- Better education and healthcare access in urban settings
- Need for improved rural healthcare infrastructure
            ''',
            'article_type': 'research',
            'author_name': 'Daniel Katey et al.',
            'author_credentials': 'Public Health Researchers',
            'author_affiliation': 'Ghana Health Research Institute',
            'publication_date': date(2024, 1, 10),
            'estimated_read_time': 10,
            'reference_link': 'https://www.tandfonline.com/doi/epdf/10.1080/16089677.2022.2074121',
            'tags': [diabetes_tag, research_tag],
            'is_featured': False
        }
    ]
    
    created_articles = []
    for article_data in diabetes_articles:
        tags = article_data.pop('tags')
        article = Article.objects.create(**article_data)
        article.tags.set(tags)
        created_articles.append(article)
        print(f"✓ Created diabetes article: {article.title}")
    
    return created_articles

def create_research_articles(tags):
    """Create research-related articles"""
    research_tag = tags['research']
    
    research_articles = [
        {
            'title': 'Artificial Intelligence in Predictive Analytics for Epidemic Outbreaks in Rural Populations',
            'summary': 'AI is transforming epidemic management in rural areas by using predictive analytics to forecast outbreaks, identify hotspots, and optimize resource allocation.',
            'content': '''
# Artificial Intelligence in Predictive Analytics for Epidemic Outbreaks

## Overview
AI is transforming epidemic management in rural areas by using predictive analytics to forecast outbreaks, identify hotspots, and optimize resource allocation.

## Key Capabilities

### Data Integration
- Integrates diverse data sources (health records, surveillance data, environmental factors)
- Detects patterns missed by traditional methods
- Works effectively even with limited local data

### Predictive Capabilities
- Forecasts disease spread patterns
- Identifies high-risk areas and populations
- Predicts outbreak timing and severity
- Guides timely intervention strategies

### Resource Optimization
- Optimizes distribution of scarce medical resources
- Improves healthcare personnel allocation
- Enhances vaccine and medication distribution

### Applications in Rural Settings
- Addresses healthcare infrastructure gaps
- Provides early warning systems
- Supports decision-making in resource-limited settings
- Improves preparedness and response capabilities

## Challenges and Solutions
- **Data Quality**: Implement robust data validation protocols
- **Infrastructure**: Develop lightweight AI models for low-resource environments
- **Training**: Provide capacity building for local healthcare workers
- **Integration**: Ensure compatibility with existing health systems

## Future Potential
- Real-time outbreak monitoring
- Automated alert systems
- Predictive resource planning
- Enhanced community health outcomes
            ''',
            'article_type': 'research',
            'author_name': 'AI Research Team',
            'author_credentials': 'Artificial Intelligence Researchers',
            'author_affiliation': 'Digital Health Institute',
            'publication_date': date(2024, 1, 25),
            'estimated_read_time': 8,
            'reference_link': 'https://www.researchgate.net/publication/epidemic_ai_rural',
            'tags': [research_tag],
            'is_featured': True
        },
        {
            'title': 'Towards a Predictive Analytics-Based Intelligent Malaria Outbreak Warning System',
            'summary': 'A mobile-based intelligent malaria outbreak early warning system that predicts outbreaks using machine learning and climatic factors.',
            'content': '''
# Intelligent Malaria Outbreak Warning System

## System Overview
This study presents a mobile-based intelligent malaria outbreak early warning system that predicts outbreaks using machine learning and climatic factors. The system targets resource-limited countries, enabling timely precautions and resource allocation.

## Key Features

### Predictive Capabilities
- Uses machine learning algorithms for outbreak prediction
- Integrates climatic factors for accurate forecasting
- Provides early warning capabilities for healthcare providers
- Enables proactive resource allocation

### Technical Innovation
- First publicly available application of its kind
- Mobile-based platform for accessibility
- Real-time data processing and analysis
- User-friendly interface for healthcare workers

### Ecological Insights
- Introduces new ecosystem model for malaria transmission
- Identifies three key confounding factors affecting incidence
- Enhances understanding of environmental influences
- Improves prediction accuracy

### Applications
- Hospital resource planning
- Health organization preparedness
- Community awareness and prevention
- Government policy and intervention timing

## Impact
- Reduces response time to outbreaks
- Improves resource utilization
- Enhances public health preparedness
- Supports evidence-based decision making
            ''',
            'article_type': 'research',
            'author_name': 'Digital Health Research Team',
            'author_credentials': 'Machine Learning Specialists',
            'author_affiliation': 'Health Technology Institute',
            'publication_date': date(2024, 2, 10),
            'estimated_read_time': 10,
            'reference_link': 'https://www.researchgate.net/publication/malaria_warning_system',
            'tags': [research_tag],
            'is_featured': False
        },
        {
            'title': 'Machine Learning Based Predictive Modelling for Disease Outbreak Threshold Estimation',
            'summary': 'A machine learning-based malaria outbreak prediction system using mosquito species data and environmental features.',
            'content': '''
# Machine Learning Based Disease Outbreak Prediction

## System Overview
This work develops a machine learning-based malaria outbreak prediction system using mosquito species data and environmental features, addressing the delays and limitations of manual diagnosis and surveillance.

## Technical Approach

### Data Sources
- Mosquito species distribution data
- Environmental features and climatic factors
- Historical outbreak patterns
- Vector population dynamics

### Machine Learning Models
- **Decision Tree Regressor**: Provides interpretable predictions
- **Multi-Layer Perceptron Regressor (MLPR)**: Achieves R² score of 0.9494
- Ensemble methods for improved accuracy
- Cross-validation for model robustness

### Key Advantages
- Replaces slow, manual diagnosis methods
- Addresses data deficiency in traditional approaches
- Provides scalable, data-driven framework
- Enables proactive prevention strategies

## Applications

### Resource Allocation
- Optimizes healthcare resource distribution
- Guides intervention timing and location
- Improves emergency response planning
- Enhances public health preparedness

### Risk Assessment
- Species-specific risk evaluation
- Geographic hotspot identification
- Seasonal pattern recognition
- Environmental factor analysis

### Public Health Impact
- Strengthens public health response
- Reduces malaria impact in endemic regions
- Improves community health outcomes
- Supports evidence-based policy making
            ''',
            'article_type': 'research',
            'author_name': 'Machine Learning Research Team',
            'author_credentials': 'Data Scientists',
            'author_affiliation': 'Computational Health Institute',
            'publication_date': date(2024, 1, 30),
            'estimated_read_time': 12,
            'reference_link': 'https://scholar.google.com/machine_learning_malaria',
            'tags': [research_tag],
            'is_featured': False
        }
    ]
    
    created_articles = []
    for article_data in research_articles:
        tags = article_data.pop('tags')
        article = Article.objects.create(**article_data)
        article.tags.set(tags)
        created_articles.append(article)
        print(f"✓ Created research article: {article.title}")
    
    return created_articles

def create_research_papers(articles):
    """Create research paper entries for research-type articles"""
    research_papers = []
    
    for article in articles:
        if article.article_type == 'research':
            # Create research paper entry
            research_paper = ResearchPaper.objects.create(
                article=article,
                paper_type='systematic_review' if 'review' in article.title.lower() else 'other',
                abstract=article.summary,
                keywords=['health', 'research', 'public health', 'epidemiology'],
                methodology='Systematic review and meta-analysis of existing literature',
                sample_size=None,
                study_duration='Variable based on included studies',
                key_findings=article.summary,
                conclusions='Further research needed in identified areas',
                limitations='Limited to available literature and data quality',
                journal_name='Various peer-reviewed journals',
                volume_issue='Multiple volumes and issues',
                page_numbers='Various',
                impact_factor=None,
                citation_count=0,
                references=[],
                h_index=0,
                research_quality_score=85.0,
                funding_source='Various funding sources',
                ethical_approval='Not applicable for review studies'
            )
            research_papers.append(research_paper)
            print(f"✓ Created research paper for: {article.title}")
    
    return research_papers

def main():
    """Main function to run the seeding process"""
    print("🌱 Starting database seeding process...")
    print("=" * 50)
    
    try:
        # Create tags
        print("\n📝 Creating article tags...")
        tags = create_tags()
        
        # Create articles
        print("\n📰 Creating malaria articles...")
        malaria_articles = create_malaria_articles(tags)
        
        print("\n📰 Creating diabetes articles...")
        diabetes_articles = create_diabetes_articles(tags)
        
        print("\n📰 Creating research articles...")
        research_articles = create_research_articles(tags)
        
        # Create research papers
        print("\n🔬 Creating research paper entries...")
        all_articles = malaria_articles + diabetes_articles + research_articles
        research_papers = create_research_papers(all_articles)
        
        # Summary
        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print(f"📊 Created {len(tags)} tags")
        print(f"📰 Created {len(all_articles)} articles")
        print(f"🔬 Created {len(research_papers)} research paper entries")
        print("\n🎉 Your database is now populated with sample data!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 