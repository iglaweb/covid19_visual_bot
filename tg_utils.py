import io
import logging
import matplotlib.pyplot as plt
import telegram

from matplotlib.figure import Figure

import io_utils
from models import GraphType, Country


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def send_photo_file(tg_bot: telegram.Bot, photo_stream, chat_id):
    tg_bot.send_photo(chat_id=chat_id, photo=photo_stream)


def send_photo_fig(tg_bot: telegram.Bot, fig: Figure, chat_id: int, graph_type: GraphType,
                   country: Country = None):
    try:
        logger.info('Sending an image..', extra={'bot': True, 'figure': plt.gcf()})
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)  # have to put the stream pointer back to zero before sending
        tg_bot.send_photo(chat_id=chat_id, photo=buffer)
        buffer.close()

        # save photo to disk
        photo_url = io_utils.get_photo_path_url(graph_type=graph_type, country=country)
        fig.savefig(photo_url)  # write image to file

        # clear RuntimeWarning: More than 20 figures have been opened. Figures created through the pyplot
        # interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much
        # memory
        plt.cla()
        plt.close(fig)
    except Exception as e:
        # if things went wrong
        logger.error('Error ocurred: "%s"', e)
