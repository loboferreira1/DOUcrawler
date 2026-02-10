import argparse
import sys
import time
import datetime
import structlog
from src import config, downloader, parser, matcher, storage, scheduler

logger = structlog.get_logger()

def job_process_dou():
    """
    Função principal do job:
    1. Carrega configuração.
    2. Itera sobre seções.
    3. Busca URLs -> Conteúdo.
    4. Analisa, Corresponde, Salva.
    """
    try:
        cfg = config.load_config()
        date_today = datetime.date.today()
        
        logger.info("job_started", date=str(date_today), keywords_count=len(cfg.keywords))
        
        if not cfg.keywords:
            logger.warning("no_keywords_configured")
            return

        for section in cfg.sections:
            logger.info("processing_section", section=section)
            try:
                urls = downloader.fetch_article_urls(section, date_today)
                for url in urls:
                    try:
                        html = downloader.fetch_content(url)
                        
                        # Análise (Parsing)
                        title = parser.extract_title(html)
                        # Precisamos do texto cru para contexto, Normalizado para correspondência
                        text_raw = parser.extract_text(html)
                        
                        # Correspondência (Matching)
                        matches = matcher.find_matches(
                            text=text_raw, 
                            keywords=cfg.keywords,
                            date=date_today.isoformat(),
                            section=section,
                            url=url,
                            title=title
                        )
                        
                        if matches:
                            logger.info("matches_found", url=url, count=len(matches))
                            for match in matches:
                                storage.save_match(match, cfg.storage)
                                logger.info("match_saved", keyword=match.keyword)
                            
                    except Exception as e:
                         logger.error("article_processing_failed", url=url, error=str(e))
                         
            except Exception as e:
                logger.error("section_processing_failed", section=section, error=str(e))

        logger.info("job_finished")

    except Exception as e:
        logger.critical("job_crashed", error=str(e))

def main():
    """Ponto de entrada."""
    parser = argparse.ArgumentParser(description="Serviço Raspador DOU")
    parser.add_argument("--run-now", action="store_true", help="Executa o raspador imediatamente para hoje e sai")
    args = parser.parse_args()

    logger.info("service_starting", mode="manual" if args.run_now else "daemon")
    
    try:
        cfg = config.load_config()
        config.setup_logging(cfg)
    except Exception as e:
        print(f"Falha ao carregar configuração ou configurar log: {e}")
        return

    if args.run_now:
        logger.info("manual_run_triggered")
        job_process_dou()
        logger.info("manual_run_completed")
        return

    sched = scheduler.create_scheduler()
    
    # Agenda o job
    try:
        h, m = map(int, cfg.schedule.time.split(":"))
        scheduler.schedule_daily_job(sched, job_process_dou, hour=h, minute=m)
        logger.info("schedule_configured", time=cfg.schedule.time)
    except Exception:
        logger.error("invalid_schedule_time", time=cfg.schedule.time, default="06:00")
        scheduler.schedule_daily_job(sched, job_process_dou, hour=6, minute=0)
    
    scheduler.start_scheduler(sched)
    
    # Mantém vivo
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("service_stopping")
        sched.shutdown()

if __name__ == "__main__":
    main()
