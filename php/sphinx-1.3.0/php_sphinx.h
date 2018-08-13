/*
  +----------------------------------------------------------------------+
  | PHP Version 5                                                        |
  +----------------------------------------------------------------------+
  | Copyright (c) 1997-2008 The PHP Group                                |
  +----------------------------------------------------------------------+
  | This source file is subject to version 3.01 of the PHP license,      |
  | that is bundled with this package in the file LICENSE, and is        |
  | available through the world-wide-web at the following url:           |
  | http://www.php.net/license/3_01.txt                                  |
  | If you did not receive a copy of the PHP license and are unable to   |
  | obtain it through the world-wide-web, please send a note to          |
  | license@php.net so we can mail you a copy immediately.               |
  +----------------------------------------------------------------------+
  | Author: Antony Dovgal <tony at daylessday.org>                       |
  | Based on Sphinx PHP API by Andrew Aksyonoff <shodan at shodan.ru>    |
  +----------------------------------------------------------------------+
*/

/* $Id: php_sphinx.h 329997 2013-04-04 11:54:20Z tony2001 $ */

#ifndef PHP_SPHINX_H
#define PHP_SPHINX_H

extern zend_module_entry sphinx_module_entry;
#define phpext_sphinx_ptr &sphinx_module_entry

#ifdef ZTS
#include "TSRM.h"
#endif

PHP_MINIT_FUNCTION(sphinx);
PHP_MINFO_FUNCTION(sphinx);

#define PHP_SPHINX_VERSION "1.3.0"

#endif	/* PHP_SPHINX_H */

/*
 * Local variables:
 * tab-width: 4
 * c-basic-offset: 4
 * End:
 * vim600: noet sw=4 ts=4 fdm=marker
 * vim<600: noet sw=4 ts=4
 */
