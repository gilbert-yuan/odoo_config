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

/* $Id: sphinx.c 327696 2012-09-19 07:56:07Z tony2001 $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "php.h"
#include "php_ini.h"
#include "ext/standard/info.h"
#include "ext/standard/file.h"
#include "zend_operators.h"
#include "php_sphinx.h"

#include <sphinxclient.h>

static zend_class_entry *ce_sphinx_client;

static zend_object_handlers php_sphinx_client_handlers;
static zend_object_handlers cannot_be_cloned;

typedef struct _php_sphinx_client {
	zend_object std;
	sphinx_client *sphinx;
	zend_bool array_result;
} php_sphinx_client;

#ifdef COMPILE_DL_SPHINX
ZEND_GET_MODULE(sphinx)
#endif

#ifndef E_RECOVERABLE_ERROR
#define E_RECOVERABLE_ERROR E_WARNING
#endif

#define SPHINX_CONST(name) REGISTER_LONG_CONSTANT(#name, name, CONST_CS | CONST_PERSISTENT)

#define SPHINX_INITIALIZED(c) \
		if (!(c) || !(c)->sphinx) { \
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "using uninitialized SphinxClient object"); \
			RETURN_FALSE; \
		}

static void php_sphinx_client_obj_dtor(void *object TSRMLS_DC) /* {{{ */
{
	php_sphinx_client *c = (php_sphinx_client *)object;

	sphinx_destroy(c->sphinx);
	zend_object_std_dtor(&c->std TSRMLS_CC);
	efree(c);
}
/* }}} */

static zend_object_value php_sphinx_client_new(zend_class_entry *ce TSRMLS_DC) /* {{{ */
{
	php_sphinx_client *c;
	zend_object_value retval;
#if PHP_VERSION_ID < 50399
	zval *tmp;
#endif

	c = ecalloc(1, sizeof(*c));
	zend_object_std_init(&c->std, ce TSRMLS_CC);

	ALLOC_HASHTABLE(c->std.properties);
	zend_hash_init(c->std.properties, 0, NULL, ZVAL_PTR_DTOR, 0);
#if PHP_VERSION_ID < 50399
	zend_hash_copy(c->std.properties, &ce->default_properties, (copy_ctor_func_t) zval_add_ref, (void *) &tmp, sizeof(zval *));
#else
	object_properties_init(&c->std, ce);
#endif
	retval.handle = zend_objects_store_put(c, (zend_objects_store_dtor_t)zend_objects_destroy_object, php_sphinx_client_obj_dtor, NULL TSRMLS_CC);
	retval.handlers = &php_sphinx_client_handlers;
	return retval;
}
/* }}} */

#if PHP_MAJOR_VERSION >= 5 && PHP_MINOR_VERSION >= 4
static zval *php_sphinx_client_read_property(zval *object, zval *member, int type, const zend_literal *key TSRMLS_DC) /* {{{ */
#else
static zval *php_sphinx_client_read_property(zval *object, zval *member, int type TSRMLS_DC) /* {{{ */
#endif
{
	php_sphinx_client *c;
	zval tmp_member;
	zval *retval;
	zend_object_handlers *std_hnd;

	c = (php_sphinx_client *)zend_object_store_get_object(object TSRMLS_CC);

	if (member->type != IS_STRING) {
		tmp_member = *member;
		zval_copy_ctor(&tmp_member);
		convert_to_string(&tmp_member);
		member = &tmp_member;
	}

	/* XXX we can either create retval ourselves (for custom properties) or use standard handlers */

	std_hnd = zend_get_std_object_handlers();
#if PHP_MAJOR_VERSION >= 5 && PHP_MINOR_VERSION >= 4
	retval = std_hnd->read_property(object, member, type, key TSRMLS_CC);
#else
	retval = std_hnd->read_property(object, member, type TSRMLS_CC);
#endif

	if (member == &tmp_member) {
		zval_dtor(member);
	}
	return retval;
}
/* }}} */

static HashTable *php_sphinx_client_get_properties(zval *object TSRMLS_DC) /* {{{ */
{
	php_sphinx_client *c;
	const char *warning, *error;
	zval *tmp;

	c = (php_sphinx_client *)zend_objects_get_address(object TSRMLS_CC);

	error = sphinx_error(c->sphinx);
	MAKE_STD_ZVAL(tmp);
	ZVAL_STRING(tmp, (char *)error, 1);
	zend_hash_update(c->std.properties, "error", sizeof("error"), (void *)&tmp, sizeof(zval *), NULL);

	warning = sphinx_warning(c->sphinx);
	MAKE_STD_ZVAL(tmp);
	ZVAL_STRING(tmp, (char *)warning, 1);
	zend_hash_update(c->std.properties, "warning", sizeof("warning"), (void *)&tmp, sizeof(zval *), NULL);
	return c->std.properties;
}
/* }}} */

#ifdef TONY_200807015
static inline void php_sphinx_error(php_sphinx_client *c TSRMLS_DC) /* {{{ */
{
	const char *err;

	err = sphinx_error(c->sphinx);
	if (!err || err[0] == '\0') {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "unknown error");
	} else {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "%s", err);
	}
}
/* }}} */
#endif

static void php_sphinx_result_to_array(php_sphinx_client *c, sphinx_result *result, zval **array TSRMLS_DC) /* {{{ */
{
	zval *tmp, *tmp_element, *sub_element, *sub_sub_element;
	int i, j;

	array_init(*array);

	/* error */
	if (!result->error) {
		add_assoc_string_ex(*array, "error", sizeof("error"), "", 1);
	} else {
		add_assoc_string_ex(*array, "error", sizeof("error"), (char *)(result->error), 1);
	}
	
	/* warning */
	if (!result->warning) {
		add_assoc_string_ex(*array, "warning", sizeof("warning"), "", 1);
	} else {
		add_assoc_string_ex(*array, "warning", sizeof("warning"), (char *)result->warning, 1);
	}
	
	/* status */
	add_assoc_long_ex(*array, "status", sizeof("status"), result->status);

	switch(result->status) {
		case SEARCHD_OK:
			/* ok, continue reading data */
			break;
		case SEARCHD_WARNING:
			/* this seems to be safe, too */
			break;
		default: 
			/* libsphinxclient doesn't nullify the data 
			   in case of error, so it's not safe to continue. */
			return;
	}

	/* fields */
	MAKE_STD_ZVAL(tmp);
	array_init(tmp);

	for (i = 0; i < result->num_fields; i++) {
		add_next_index_string(tmp, result->fields[i], 1);
	}
	add_assoc_zval_ex(*array, "fields", sizeof("fields"), tmp);

	/* attrs */
	MAKE_STD_ZVAL(tmp);
	array_init(tmp);

	for (i = 0; i < result->num_attrs; i++) {
#if SIZEOF_LONG == 8
		add_assoc_long_ex(tmp, result->attr_names[i], strlen(result->attr_names[i]) + 1, result->attr_types[i]);
#else
		double float_value;
		char buf[128];

		float_value = (double)result->attr_types[i];
		slprintf(buf, sizeof(buf), "%.0f", float_value);
		add_assoc_string_ex(tmp, result->attr_names[i], strlen(result->attr_names[i]) + 1, buf, 1);
#endif
	}
	add_assoc_zval_ex(*array, "attrs", sizeof("attrs"), tmp);

	/* matches */
	if (result->num_matches) {
		MAKE_STD_ZVAL(tmp);
		array_init(tmp);

		for (i = 0; i < result->num_matches; i++) {
			MAKE_STD_ZVAL(tmp_element);
			array_init(tmp_element);

			if (c->array_result) {
				/* id */
#if SIZEOF_LONG == 8
				add_assoc_long_ex(tmp_element, "id", sizeof("id"), sphinx_get_id(result, i));
#else
				double float_id;
				char buf[128];

				float_id = (double)sphinx_get_id(result, i);
				slprintf(buf, sizeof(buf), "%.0f", float_id);
				add_assoc_string_ex(tmp_element, "id", sizeof("id"), buf, 1);
#endif
			}

			/* weight */
			add_assoc_long_ex(tmp_element, "weight", sizeof("weight"), sphinx_get_weight(result, i));

			/* attrs */
			MAKE_STD_ZVAL(sub_element);
			array_init(sub_element);

			for (j = 0; j < result->num_attrs; j++) {
#if SIZEOF_LONG != 8
				double float_value;
				char buf[128];
#endif

				MAKE_STD_ZVAL(sub_sub_element);

				switch(result->attr_types[j]) {
					case SPH_ATTR_MULTI | SPH_ATTR_INTEGER:
						{
							int k;
							unsigned int *mva = sphinx_get_mva(result, i, j);
							unsigned int tmp, num;

							array_init(sub_sub_element);

							if (!mva) {
								break;
							}

							memcpy(&num, mva, sizeof(unsigned int));

							for (k = 1; k <= num; k++) {
								mva++;
								memcpy(&tmp, mva, sizeof(unsigned int));
#if SIZEOF_LONG == 8
								add_next_index_long(sub_sub_element, tmp);
#else
								float_value = (double)tmp;
								slprintf(buf, sizeof(buf), "%.0f", float_value);
								add_next_index_string(sub_sub_element, buf, 1);
#endif
							}
						}	break;

					case SPH_ATTR_FLOAT:
						ZVAL_DOUBLE(sub_sub_element, sphinx_get_float(result, i, j));
						break;
#if LIBSPHINX_VERSION_ID >= 110
					case SPH_ATTR_STRING:
						ZVAL_STRING(sub_sub_element, sphinx_get_string(result, i, j), 1);
						break;                        
#endif
					default:
#if SIZEOF_LONG == 8
						ZVAL_LONG(sub_sub_element, sphinx_get_int(result, i, j));
#else
						float_value = (double)sphinx_get_int(result, i, j);
						slprintf(buf, sizeof(buf), "%.0f", float_value);
						ZVAL_STRING(sub_sub_element, buf, 1);
#endif
						break;
				}

				add_assoc_zval(sub_element, result->attr_names[j], sub_sub_element);
			}

			add_assoc_zval_ex(tmp_element, "attrs", sizeof("attrs"), sub_element);

			if (c->array_result) {
				add_next_index_zval(tmp, tmp_element);
			} else {
#if SIZEOF_LONG == 8
				add_index_zval(tmp, sphinx_get_id(result, i), tmp_element);
#else
				char buf[128];
				double float_id;
				int buf_len;

				float_id = (double)sphinx_get_id(result, i);
				buf_len = slprintf(buf, sizeof(buf), "%.0f", float_id);
				add_assoc_zval_ex(tmp, buf, buf_len + 1, tmp_element);
#endif
			}
		}

		add_assoc_zval_ex(*array, "matches", sizeof("matches"), tmp);
	}

	/* total */
	add_assoc_long_ex(*array, "total", sizeof("total"), result->total);

	/* total_found */
	add_assoc_long_ex(*array, "total_found", sizeof("total_found"), result->total_found);
	
	/* time */
	add_assoc_double_ex(*array, "time", sizeof("time"), (double)result->time_msec/1000.0);

	/* words */
	if (result->num_words) {
		MAKE_STD_ZVAL(tmp);
		array_init(tmp);
		for (i = 0; i < result->num_words; i++) {
			MAKE_STD_ZVAL(sub_element);
			array_init(sub_element);

			add_assoc_long_ex(sub_element, "docs", sizeof("docs"), result->words[i].docs);
			add_assoc_long_ex(sub_element, "hits", sizeof("hits"), result->words[i].hits);
			add_assoc_zval_ex(tmp, (char *)result->words[i].word, strlen(result->words[i].word) + 1, sub_element);
		}
		add_assoc_zval_ex(*array, "words", sizeof("words"), tmp);
	}
}
/* }}} */


/* {{{ proto void SphinxClient::__construct() */
static PHP_METHOD(SphinxClient, __construct)
{
	php_sphinx_client *c;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);

	if (c->sphinx) {
		/* called __construct() twice, bail out */
		return;
	}

	c->sphinx = sphinx_create(1 /* copy string args */);
	
	sphinx_set_connect_timeout(c->sphinx, FG(default_socket_timeout));
}
/* }}} */

/* {{{ proto bool SphinxClient::setServer(string server, int port) */
static PHP_METHOD(SphinxClient, setServer)
{
	php_sphinx_client *c;
	long port;
	char *server;
	int server_len, res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "sl", &server, &server_len, &port) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_server(c->sphinx, server, (int)port);
	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */
 
/* {{{ proto bool SphinxClient::setLimits(int offset, int limit[, int max_matches[, int cutoff]]) */
static PHP_METHOD(SphinxClient, setLimits)
{
	php_sphinx_client *c;
	long offset, limit, max_matches = 0, cutoff = 0;
	int res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll|ll", &offset, &limit, &max_matches, &cutoff) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_limits(c->sphinx, (int)offset, (int)limit, (int)max_matches, (int)cutoff);
	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setMatchMode(int mode) */
static PHP_METHOD(SphinxClient, setMatchMode)
{
	php_sphinx_client *c;
	long mode;
	int res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &mode) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)
	
	res = sphinx_set_match_mode(c->sphinx, mode);
	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setIndexWeights(array weights) */
static PHP_METHOD(SphinxClient, setIndexWeights)
{
	php_sphinx_client *c;
	zval *weights, **item;
	int num_weights, res = 0, i;
	int *index_weights;
	char **index_names;
	char *string_key;
	unsigned int string_key_len;
	unsigned long int num_key;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "a", &weights) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)
	
	num_weights = zend_hash_num_elements(Z_ARRVAL_P(weights));
	if (!num_weights) {
		/* check for empty array and return false right away */
		RETURN_FALSE;
	}

	index_names = safe_emalloc(num_weights, sizeof(char *), 0);
	index_weights = safe_emalloc(num_weights, sizeof(int), 0);

	/* reset num_weights, we'll reuse it count _real_ number of entries */
	num_weights = 0;

	for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(weights)); 
		 zend_hash_get_current_data(Z_ARRVAL_P(weights), (void **)&item) != FAILURE;
		 zend_hash_move_forward(Z_ARRVAL_P(weights))) {
		
		if (zend_hash_get_current_key_ex(Z_ARRVAL_P(weights), &string_key, &string_key_len, &num_key, 0, NULL) != HASH_KEY_IS_STRING) {
			/* if the key is not string.. well.. you're screwed */
			break;
		}

		convert_to_long_ex(item);
		
		index_names[num_weights] = estrndup(string_key, string_key_len);
		index_weights[num_weights] = Z_LVAL_PP(item);

		num_weights++;
	}

	if (num_weights) {
		res = sphinx_set_index_weights(c->sphinx, num_weights, (const char **)index_names, index_weights);
	}

	for (i = 0; i != num_weights; i++) {
		efree(index_names[i]);
	}
	efree(index_names);
	efree(index_weights);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

#if LIBSPHINX_VERSION_ID >= 99
/* {{{ proto bool SphinxClient::setSelect(string clause) */
static PHP_METHOD(SphinxClient, setSelect)
{
	php_sphinx_client *c;
	char *clause;
	int clause_len, res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "s", &clause, &clause_len) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_select(c->sphinx, clause);
	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */
#endif

/* {{{ proto bool SphinxClient::setIDRange(int min, int max) */
static PHP_METHOD(SphinxClient, setIDRange)
{
	php_sphinx_client *c;
	long min, max;
	int res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &min, &max) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_id_range(c->sphinx, (sphinx_uint64_t)min, (sphinx_uint64_t)max);
	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setFilter(string attribute, array values[, bool exclude]) */
static PHP_METHOD(SphinxClient, setFilter)
{
	php_sphinx_client *c;
	zval *values, **item;
	char *attribute;
	int	attribute_len, num_values, i = 0, res;
	zend_bool exclude = 0;
	sphinx_int64_t *u_values;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "sa|b", &attribute, &attribute_len, &values, &exclude) == FAILURE) {
		return;
	}
	
	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	num_values = zend_hash_num_elements(Z_ARRVAL_P(values));
	if (!num_values) {
		RETURN_FALSE;
	}

	u_values = safe_emalloc(num_values, sizeof(sphinx_int64_t), 0);

	for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(values));
		 zend_hash_get_current_data(Z_ARRVAL_P(values), (void **) &item) != FAILURE;
		 zend_hash_move_forward(Z_ARRVAL_P(values))) {
		
		convert_to_double_ex(item);
		u_values[i] = (sphinx_int64_t)Z_DVAL_PP(item);
		i++;
	}

	res = sphinx_add_filter(c->sphinx, attribute, num_values, u_values, exclude ? 1 : 0);
	efree(u_values);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setFilterRange(string attribute, int min, int max[, bool exclude]) */
static PHP_METHOD(SphinxClient, setFilterRange)
{
	php_sphinx_client *c;
	char *attribute;
	int attribute_len, res;
	long min, max;
	zend_bool exclude = 0;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "sll|b", &attribute, &attribute_len, &min, &max, &exclude ) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_add_filter_range(c->sphinx, attribute, min, max, exclude);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setFilterFloatRange(string attribute, float min, float max[, bool exclude]) */
static PHP_METHOD(SphinxClient, setFilterFloatRange)
{
	php_sphinx_client *c;
	char *attribute;
	int attribute_len, res;
	double min, max;
	zend_bool exclude = 0;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "sdd|b", &attribute, &attribute_len, &min, &max, &exclude) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_add_filter_float_range(c->sphinx, attribute, min, max, exclude);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setGeoAnchor(string attrlat, string attrlong, float latitude, float longitude) */
static PHP_METHOD(SphinxClient, setGeoAnchor)
{
	php_sphinx_client *c;
	char *attrlat, *attrlong;
	int attrlat_len, attrlong_len, res;
	double latitude, longitude;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ssdd", &attrlat, &attrlat_len, &attrlong, &attrlong_len, &latitude, &longitude) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_geoanchor(c->sphinx, attrlat, attrlong, latitude, longitude);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setGroupBy(string attribute, int func[, string groupsort]) */
static PHP_METHOD(SphinxClient, setGroupBy)
{
	php_sphinx_client *c;
	char *attribute, *groupsort = NULL;
	int attribute_len, groupsort_len, func, res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "sl|s", &attribute, &attribute_len, &func, &groupsort, &groupsort_len) == FAILURE) {
		return;
	}
	
	if (groupsort == NULL) {
		groupsort = "@group desc";
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_groupby(c->sphinx, attribute, func, groupsort);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setGroupDistinct(string attribute) */
static PHP_METHOD(SphinxClient, setGroupDistinct)
{
	php_sphinx_client *c;
	char *attribute;
	int attribute_len, res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "s", &attribute, &attribute_len) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_groupby_distinct(c->sphinx, attribute);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setRetries(int count[, int delay]) */
static PHP_METHOD(SphinxClient, setRetries)
{
	php_sphinx_client *c;
	long count, delay = 0;
	int res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l|l", &count, &delay) == FAILURE) {
		return; 
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_retries(c->sphinx, (int)count, (int)delay);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setMaxQueryTime(int qtime) */
static PHP_METHOD(SphinxClient, setMaxQueryTime)
{
	php_sphinx_client *c;
	long qtime;
	int res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &qtime) == FAILURE) {
		return;	
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_max_query_time(c->sphinx, (int)qtime);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

#ifdef HAVE_3ARG_SPHINX_SET_RANKING_MODE
/* {{{ proto bool SphinxClient::setRankingMode(int ranker[, string ranking_expression]) */
static PHP_METHOD(SphinxClient, setRankingMode)
{
	php_sphinx_client *c;
	long ranker;
	int res, rank_expr_len;
	char *rank_expr = NULL;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l|s", &ranker, &rank_expr, &rank_expr_len) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_ranking_mode(c->sphinx, (int)ranker, rank_expr);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */
#else
/* {{{ proto bool SphinxClient::setRankingMode(int ranker) */
static PHP_METHOD(SphinxClient, setRankingMode)
{
	php_sphinx_client *c;
	long ranker;
	int res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &ranker) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_ranking_mode(c->sphinx, (int)ranker);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */
#endif

/* {{{ proto bool SphinxClient::setFieldWeights(array weights) */
static PHP_METHOD(SphinxClient, setFieldWeights)
{
	php_sphinx_client *c;
	zval *weights, **item;
	int num_weights, res = 0, i;
	int *field_weights;
	char **field_names;
	char *string_key;
	unsigned int string_key_len;
	unsigned long int num_key;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "a", &weights) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	num_weights = zend_hash_num_elements(Z_ARRVAL_P(weights));
	if (!num_weights) {
		/* check for empty array and return false right away */
		RETURN_FALSE;
	}

	field_names = safe_emalloc(num_weights, sizeof(char *), 0);
	field_weights = safe_emalloc(num_weights, sizeof(int), 0);

	/* reset num_weights, we'll reuse it count _real_ number of entries */
	num_weights = 0;

	for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(weights)); 
		 zend_hash_get_current_data(Z_ARRVAL_P(weights), (void **)&item) != FAILURE;
		 zend_hash_move_forward(Z_ARRVAL_P(weights))) {
		
		if (zend_hash_get_current_key_ex(Z_ARRVAL_P(weights), &string_key, &string_key_len, &num_key, 0, NULL) != HASH_KEY_IS_STRING) {
			/* if the key is not string.. well.. you're screwed */
			break;
		}

		convert_to_long_ex(item);
		
		field_names[num_weights] = estrndup(string_key, string_key_len);
		field_weights[num_weights] = Z_LVAL_PP(item);

		num_weights++;
	}

	if (num_weights) {
		res = sphinx_set_field_weights(c->sphinx, num_weights, (const char **) field_names, field_weights);
	}

	for (i = 0; i != num_weights; i++) {
		efree(field_names[i]);
	}
	efree(field_names);
	efree(field_weights);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setSortMode(int mode[, string sortby]) */
static PHP_METHOD(SphinxClient, setSortMode)
{
	php_sphinx_client *c;
	long mode;
	char *sortby = NULL;
	int sortby_len, res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l|s", &mode, &sortby, &sortby_len) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_sort_mode(c->sphinx, (int)mode, sortby); 

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::setConnectTimeout(float timeout) */
static PHP_METHOD(SphinxClient, setConnectTimeout)
{   
	php_sphinx_client *c;
	double timeout;
	int res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "d", &timeout) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_set_connect_timeout(c->sphinx, timeout);

	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}   
/* }}} */

/* {{{ proto bool SphinxClient::setArrayResult(bool array_result) */
static PHP_METHOD(SphinxClient, setArrayResult)
{
	php_sphinx_client *c;
	zend_bool array_result;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "b", &array_result) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	c->array_result = array_result; 
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto int SphinxClient::updateAttributes(string index, array attributes, array values[, bool mva]) */
static PHP_METHOD(SphinxClient, updateAttributes)
{
	php_sphinx_client *c;
	zval *attributes, *values, **item; 
	char *index;
	const char **attrs;
	int index_len, attrs_num, values_num;
	int res = 0;
	sphinx_uint64_t *docids = NULL;
	sphinx_int64_t *vals = NULL;
	unsigned int *vals_mva = NULL;
#if LIBSPHINX_VERSION_ID >= 110
	int res_mva, values_mva_num, values_mva_size = 0;
	zval **attr_value_mva;
#endif
	int a = 0, i = 0, j = 0;
	zend_bool mva = 0;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "saa|b", &index, &index_len, &attributes, &values, &mva) == FAILURE) {
		return;
	}

#if LIBSPHINX_VERSION_ID < 110
	if (mva) {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "update mva attributes is not supported");
		RETURN_FALSE;
	}
#endif

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	attrs_num = zend_hash_num_elements(Z_ARRVAL_P(attributes));

	if (!attrs_num) {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "empty attributes array passed");
		RETURN_FALSE;
	}

	values_num = zend_hash_num_elements(Z_ARRVAL_P(values));

	if (!values_num) {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "empty values array passed");
		RETURN_FALSE;
	}

	attrs = emalloc(sizeof(char *) * attrs_num);
	for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(attributes));
		 zend_hash_get_current_data(Z_ARRVAL_P(attributes), (void **) &item) != FAILURE;
		 zend_hash_move_forward(Z_ARRVAL_P(attributes))) {
		if (Z_TYPE_PP(item) != IS_STRING) {
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "non-string attributes are not allowed");
			break;
		}
		attrs[a] = Z_STRVAL_PP(item); /* no copying here! */
		a++;
	}

	/* cleanup on error */
	if (a != attrs_num) {
		RETVAL_FALSE;
		goto cleanup;
	}

	docids = emalloc(sizeof(sphinx_int64_t) * values_num);
	if (!mva) {
		vals = safe_emalloc(values_num * attrs_num, sizeof(sphinx_int64_t), 0);
	}
	for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(values));
		 zend_hash_get_current_data(Z_ARRVAL_P(values), (void **) &item) != FAILURE;
		 zend_hash_move_forward(Z_ARRVAL_P(values))) {
		char *str_id;
		ulong id;
		zval **attr_value;
		int failed = 0, key_type;
		uint str_id_len;
		double float_id = 0;
		unsigned char id_type;

		if (Z_TYPE_PP(item) != IS_ARRAY) {
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "value is not an array of attributes");
			break;
		}

		if (zend_hash_num_elements(Z_ARRVAL_PP(item)) != attrs_num) {
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "number of values is not equal to the number of attributes");
			break;
		}

		key_type = zend_hash_get_current_key_ex(Z_ARRVAL_P(values), &str_id, &str_id_len, &id, 0, NULL);

		if (key_type == HASH_KEY_IS_LONG) {
			/* ok */
			id_type = IS_LONG;
		} else if (key_type == HASH_KEY_IS_STRING) {
			id_type = is_numeric_string(str_id, str_id_len, (long *)&id, &float_id, 0);
			if (id_type == IS_LONG || id_type == IS_DOUBLE) {
				/* ok */
			} else {
				php_error_docref(NULL TSRMLS_CC, E_WARNING, "document ID must be numeric");
				break;
			}
		} else {
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "document ID must be integer");
			break;
		}
		
		if (id_type == IS_LONG) {
			docids[i] = (sphinx_uint64_t)id;
		} else { /* IS_FLOAT */
			docids[i] = (sphinx_uint64_t)float_id;
		}
		
		a = 0;
		for (zend_hash_internal_pointer_reset(Z_ARRVAL_PP(item));
				zend_hash_get_current_data(Z_ARRVAL_PP(item), (void **) &attr_value) != FAILURE;
				zend_hash_move_forward(Z_ARRVAL_PP(item))) {
			if (mva) {
#if LIBSPHINX_VERSION_ID >= 110
				if (Z_TYPE_PP(attr_value) != IS_ARRAY) {
					php_error_docref(NULL TSRMLS_CC, E_WARNING, "attribute value must be an array");
					failed = 1;
					break;
				}
				values_mva_num = zend_hash_num_elements(Z_ARRVAL_PP(attr_value));
				if (values_mva_num > values_mva_size) {
					values_mva_size = values_mva_num;
					vals_mva = safe_erealloc(vals_mva, values_mva_size, sizeof(unsigned int), 0);
				}
				if (vals_mva) {
					memset(vals_mva, 0, values_mva_size * sizeof(unsigned int));
				}
				
				j = 0;
				for (zend_hash_internal_pointer_reset(Z_ARRVAL_PP(attr_value));
						zend_hash_get_current_data(Z_ARRVAL_PP(attr_value), (void **) &attr_value_mva) != FAILURE;
						zend_hash_move_forward(Z_ARRVAL_PP(attr_value))) {
					if (Z_TYPE_PP(attr_value_mva) != IS_LONG) {
						php_error_docref(NULL TSRMLS_CC, E_WARNING, "mva attribute value must be integer");
						failed = 1;
						break;
					}
					vals_mva[j] = (unsigned int)Z_LVAL_PP(attr_value_mva);
					j++;
				}
				if (failed) {
					break;
				}

				res_mva = sphinx_update_attributes_mva(c->sphinx, index, attrs[a], docids[i], values_mva_num, vals_mva);

				if (res_mva < 0) {
					failed = 1;
					break;
				}
#endif
				a++; 
			} else {
				if (Z_TYPE_PP(attr_value) != IS_LONG) {
					php_error_docref(NULL TSRMLS_CC, E_WARNING, "attribute value must be integer");
					failed = 1;
					break;
				}
				vals[j] = (sphinx_int64_t)Z_LVAL_PP(attr_value);
				j++;
			}
		}

		if (failed) {
			break;
		}
		
		if (mva) {
			res++;
		}
		i++;
	}

	if (!mva && i != values_num) {
		RETVAL_FALSE;
		goto cleanup;
	}
	
	if (!mva) {
		res = sphinx_update_attributes(c->sphinx, index, (int)attrs_num, attrs, values_num, docids, vals); 
	}

	if (res < 0) {
		RETVAL_FALSE;
	} else {
		RETVAL_LONG(res);
	}

cleanup:
	efree(attrs);
	if (docids) {
		efree(docids);
	}
	if (vals) {
		efree(vals);
	}
	if (vals_mva) {
		efree(vals_mva);
	}
}
/* }}} */

/* {{{ proto array SphinxClient::buildExcerpts(array docs, string index, string words[, array opts]) */
static PHP_METHOD(SphinxClient, buildExcerpts)
{
	php_sphinx_client *c;
	zval *docs_array, *opts_array = NULL, **item;
	char *index, *words;
	const char **docs;
	sphinx_excerpt_options opts;
	int index_len, words_len;
	int docs_num, i = 0;
	char **result;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ass|a", &docs_array, &index, &index_len, &words, &words_len, &opts_array) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	docs_num = zend_hash_num_elements(Z_ARRVAL_P(docs_array));

	if (!docs_num) {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "empty documents array passed");
		RETURN_FALSE;
	}

	docs = emalloc(sizeof(char *) * docs_num);
	for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(docs_array));
		 zend_hash_get_current_data(Z_ARRVAL_P(docs_array), (void **) &item) != FAILURE;
		 zend_hash_move_forward(Z_ARRVAL_P(docs_array))) {
		if (Z_TYPE_PP(item) != IS_STRING) {
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "non-string documents are not allowed");
			break;
		}
		docs[i] = Z_STRVAL_PP(item); /* no copying here! */
		i++;
	}

	if (i != docs_num) {
		RETVAL_FALSE;
		goto cleanup;
	}

#define OPTS_EQUAL(str, str_len, txt) str_len == sizeof(txt) && memcmp(txt, str, sizeof(txt)) == 0 

	if (opts_array) {
		char *string_key;
		unsigned int string_key_len;
		ulong dummy;

		/* nullify everything */
		sphinx_init_excerpt_options(&opts);
		for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(opts_array));
				zend_hash_get_current_data(Z_ARRVAL_P(opts_array), (void **) &item) != FAILURE;
				zend_hash_move_forward(Z_ARRVAL_P(opts_array))) {

			switch (Z_TYPE_PP(item)) {
				case IS_STRING:
				case IS_LONG:
				case IS_BOOL:
					break;
				default:
					continue; /* ignore invalid options */
			}

			if (zend_hash_get_current_key_ex(Z_ARRVAL_P(opts_array), &string_key, &string_key_len, &dummy, 0, NULL) != HASH_KEY_IS_STRING) {
				continue; /* ignore invalid option names */
			}

			if (OPTS_EQUAL(string_key, string_key_len, "before_match")) {
				SEPARATE_ZVAL(item);
				convert_to_string_ex(item);
				opts.before_match = Z_STRVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "after_match")) {
				SEPARATE_ZVAL(item);
				convert_to_string_ex(item);
				opts.after_match = Z_STRVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "chunk_separator")) {
				SEPARATE_ZVAL(item);
				convert_to_string_ex(item);
				opts.chunk_separator = Z_STRVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "limit")) {
				SEPARATE_ZVAL(item);
				convert_to_long_ex(item);
				opts.limit = (int)Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "around")) {
				SEPARATE_ZVAL(item);
				convert_to_long_ex(item);
				opts.around = (int)Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "exact_phrase")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.exact_phrase = Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "single_passage")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.single_passage = Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "use_boundaries")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.use_boundaries = Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "weight_order")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.weight_order = Z_LVAL_PP(item);
#if LIBSPHINX_VERSION_ID >= 110
			} else if (OPTS_EQUAL(string_key, string_key_len, "query_mode")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.query_mode = Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "force_all_words")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.force_all_words = Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "limit_passages")) {
				SEPARATE_ZVAL(item);
				convert_to_long_ex(item);
				opts.limit_passages = (int)Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "limit_words")) {
				SEPARATE_ZVAL(item);
				convert_to_long_ex(item);
				opts.limit_words = (int)Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "start_passage_id")) {
				SEPARATE_ZVAL(item);
				convert_to_long_ex(item);
				opts.start_passage_id = (int)Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "load_files")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.load_files = Z_LVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "html_strip_mode")) {
				SEPARATE_ZVAL(item);
				convert_to_string_ex(item);
				opts.html_strip_mode = Z_STRVAL_PP(item);
			} else if (OPTS_EQUAL(string_key, string_key_len, "allow_empty")) {
				SEPARATE_ZVAL(item);
				convert_to_boolean_ex(item);
				opts.allow_empty = Z_LVAL_PP(item);
#endif
			} else {
				/* ignore invalid option names */
			}
		}
	}

	if (opts_array) {
		result = sphinx_build_excerpts(c->sphinx, docs_num, docs, index, words, &opts); 
	} else {
		result = sphinx_build_excerpts(c->sphinx, docs_num, docs, index, words, NULL); 
	}

	if (!result) {
		RETVAL_FALSE;
	} else {
		array_init(return_value);
		for (i = 0; i < docs_num; i++) {
			if (result[i] && result[i][0] != '\0') {
				add_next_index_string(return_value, result[i], 1);
			} else {
				add_next_index_string(return_value, "", 1);
			}
			free(result[i]);
		}
		free(result);
	}

cleanup:
	efree(docs);
}
/* }}} */

/* {{{ proto array SphinxClient::buildKeywords(string query, string index, bool hits) */
static PHP_METHOD(SphinxClient, buildKeywords)
{
	php_sphinx_client *c;
	char *query, *index;
	int query_len, index_len;
	zend_bool hits;
	sphinx_keyword_info *result;
	int i, num_keywords;
	zval *tmp;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ssb", &query, &query_len, &index, &index_len, &hits) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	result = sphinx_build_keywords(c->sphinx, query, index, hits, &num_keywords);
	if (!result || num_keywords <= 0) {
		RETURN_FALSE;
	}

	array_init(return_value);
	for (i = 0; i < num_keywords; i++) {
		MAKE_STD_ZVAL(tmp);
		array_init(tmp);
		
		add_assoc_string_ex(tmp, "tokenized", sizeof("tokenized"), result[i].tokenized, 1);
		add_assoc_string_ex(tmp, "normalized", sizeof("normalized"), result[i].normalized, 1);

		if (hits) {
			add_assoc_long_ex(tmp, "docs", sizeof("docs"), result[i].num_docs);
			add_assoc_long_ex(tmp, "hits", sizeof("hits"), result[i].num_hits);
		}

		add_next_index_zval(return_value, tmp);

		free(result[i].tokenized);
		free(result[i].normalized);
	}
	free(result);
}
/* }}} */

/* {{{ proto void SphinxClient::resetFilters() */
static PHP_METHOD(SphinxClient, resetFilters)
{
	php_sphinx_client *c;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	sphinx_reset_filters(c->sphinx);
}
/* }}} */

/* {{{ proto void SphinxClient::resetGroupBy() */
static PHP_METHOD(SphinxClient, resetGroupBy)
{
	php_sphinx_client *c;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	sphinx_reset_groupby(c->sphinx);
}
/* }}} */

/* {{{ proto string SphinxClient::getLastWarning() */
static PHP_METHOD(SphinxClient, getLastWarning)
{
	php_sphinx_client *c;
	const char *warning;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	warning = sphinx_warning(c->sphinx);
	if (!warning || !warning[0]) {
		RETURN_EMPTY_STRING();
	}
	RETURN_STRING((char *)warning, 1);
}
/* }}} */

/* {{{ proto string SphinxClient::getLastError() */
static PHP_METHOD(SphinxClient, getLastError)
{
	php_sphinx_client *c;
	const char *error;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	error = sphinx_error(c->sphinx);
	if (!error || !error[0]) {
		RETURN_EMPTY_STRING();
	}
	RETURN_STRING((char *)error, 1);
}
/* }}} */

/* {{{ proto array SphinxClient::query(string query[, string index[, string comment]]) */
static PHP_METHOD(SphinxClient, query)
{
	php_sphinx_client *c;
	char *query, *index = "*", *comment = "";
	int query_len, index_len, comment_len;
	sphinx_result *result;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "s|ss", &query, &query_len, &index, &index_len, &comment, &comment_len) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	result = sphinx_query(c->sphinx, query, index, comment);

	if (!result) {
		RETURN_FALSE;
	}

	php_sphinx_result_to_array(c, result, &return_value TSRMLS_CC);
}

/* }}} */

/* {{{ proto int SphinxClient::addQuery(string query[, string index[, string comment]]) */
static PHP_METHOD(SphinxClient, addQuery)
{
	php_sphinx_client *c;
	char *query, *index = "*", *comment = "";
	int query_len, index_len, comment_len, res;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "s|ss", &query, &query_len, &index, &index_len, &comment, &comment_len) == FAILURE) {
		return;
	}

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	res = sphinx_add_query(c->sphinx, query, index, comment);

	if (res < 0) {
		RETURN_FALSE;
	}
	RETURN_LONG(res);
}

/* }}} */

/* {{{ proto array SphinxClient::runQueries() */
static PHP_METHOD(SphinxClient, runQueries)
{
	php_sphinx_client *c;
	sphinx_result *results;
	int i, num_results;
	zval *single_result;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)

	results = sphinx_run_queries(c->sphinx);

	if (!results) {
		RETURN_FALSE;
	}

	num_results = sphinx_get_num_results(c->sphinx);

	array_init(return_value);
	for (i = 0; i < num_results; i++) {
		MAKE_STD_ZVAL(single_result);
		php_sphinx_result_to_array(c, &results[i], &single_result TSRMLS_CC);
		add_next_index_zval(return_value, single_result);
	}
}
/* }}} */

/* {{{ proto string SphinxClient::escapeString(string data) */
static PHP_METHOD(SphinxClient, escapeString)
{
	char *str, *new_str, *source, *target;
	int str_len, new_str_len, i;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "s", &str, &str_len) == FAILURE) {
		return;
	}
	
	if (!str_len) {
		RETURN_EMPTY_STRING();
	}

	new_str = safe_emalloc(2, str_len, 1);
	target = new_str;
	source = str;
	for (i = 0; i < str_len; i++) {
		switch (*source) {
			case '(':
			case ')':
			case '|':
			case '-':
			case '!':
			case '@':
			case '~':
			case '"':
			case '&':
			case '/':
			case '\\':
				*target++ = '\\';
				*target++ = *source;
				break;
			default:
				*target++ = *source;
				break;
		}
		source++;
	}
	*target = '\0';

	new_str_len = target - new_str;
	new_str = erealloc(new_str, new_str_len + 1);
	RETURN_STRINGL(new_str, new_str_len, 0);
}
/* }}} */

#if LIBSPHINX_VERSION_ID >= 99
/* {{{ proto bool SphinxClient::open() */
static PHP_METHOD(SphinxClient, open)
{
	php_sphinx_client *c;
	int res;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)
	
	res = sphinx_open(c->sphinx);
	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto bool SphinxClient::close() */
static PHP_METHOD(SphinxClient, close)
{
	php_sphinx_client *c;
	int res;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)
	
	res = sphinx_close(c->sphinx);
	if (!res) {
		RETURN_FALSE;
	}
	RETURN_TRUE;
}
/* }}} */

/* {{{ proto array SphinxClient::status() */
static PHP_METHOD(SphinxClient, status)
{
	php_sphinx_client *c;
	char **result;
	int i, j, k, num_rows, num_cols;
	zval *tmp;

	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)
	
	result = sphinx_status(c->sphinx, &num_rows, &num_cols);
	
	if (!result || num_rows <= 0) {
		RETURN_FALSE;
	}
	
	k = 0;
	array_init(return_value);
	for (i = 0; i < num_rows; i++) {
		MAKE_STD_ZVAL(tmp);
		array_init(tmp);
		
		for (j = 0; j < num_cols; j++, k++) {
			add_next_index_string(tmp, result[k], 1);
		}
		add_next_index_zval(return_value, tmp);
	}
	sphinx_status_destroy(result, num_rows, num_cols);
}
/* }}} */

/* {{{ proto bool SphinxClient::setOverride(string attribute, int type, array values) */
static PHP_METHOD(SphinxClient, setOverride)
{
	php_sphinx_client *c;
	zval *values, **attr_value;
	char *attribute;
	int attribute_len, type, values_num, i = 0;
	int res;
	sphinx_uint64_t *docids = NULL; 
	unsigned int *vals = NULL;

	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "sla", &attribute, &attribute_len, &type, &values) == FAILURE) {
		return;
	}
	
	c = (php_sphinx_client *)zend_object_store_get_object(getThis() TSRMLS_CC);
	SPHINX_INITIALIZED(c)
	
	if (type != SPH_ATTR_INTEGER && type != SPH_ATTR_TIMESTAMP
		&& type != SPH_ATTR_BOOL && type != SPH_ATTR_FLOAT) {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "type must be scalar");
		RETURN_FALSE;
	}
	
	values_num = zend_hash_num_elements(Z_ARRVAL_P(values));
	if (!values_num) {
		php_error_docref(NULL TSRMLS_CC, E_WARNING, "empty values array passed");
		RETURN_FALSE;
	}
	
	docids = emalloc(sizeof(sphinx_uint64_t) * values_num);
	vals = safe_emalloc(values_num, sizeof(unsigned int), 0);
	for (zend_hash_internal_pointer_reset(Z_ARRVAL_P(values));
		 zend_hash_get_current_data(Z_ARRVAL_P(values), (void **) &attr_value) != FAILURE;
		 zend_hash_move_forward(Z_ARRVAL_P(values))) 
	{
		char *str_id;
		ulong id;
		int key_type;
		uint str_id_len;
		double float_id = 0;
		unsigned char id_type;

		if (Z_TYPE_PP(attr_value) != IS_LONG) {
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "attribute value must be integer");
			break;
		}

		key_type = zend_hash_get_current_key_ex(Z_ARRVAL_P(values), &str_id, &str_id_len, &id, 0, NULL);

		if (key_type == HASH_KEY_IS_LONG) {
			/* ok */
			id_type = IS_LONG;
		} else if (key_type == HASH_KEY_IS_STRING) {
			id_type = is_numeric_string(str_id, str_id_len, (long *)&id, &float_id, 0);
			if (id_type == IS_LONG || id_type == IS_DOUBLE) {
				/* ok */
			} else {
				php_error_docref(NULL TSRMLS_CC, E_WARNING, "document ID must be numeric");
				break;
			}
		} else {
			php_error_docref(NULL TSRMLS_CC, E_WARNING, "document ID must be integer");
			break;
		}
		vals[i] = (sphinx_uint64_t)Z_LVAL_PP(attr_value);

		if (id_type == IS_LONG) {
			docids[i] = (sphinx_uint64_t)id;
		} else { /* IS_FLOAT */
			docids[i] = (sphinx_uint64_t)float_id;
		}
		i++;
	}

	if (i != values_num) {
		RETVAL_FALSE;
		goto cleanup;
	}
	
	res = sphinx_add_override(c->sphinx, attribute, docids, values_num, vals); 
	if (!res) {
		RETVAL_FALSE;
	} else {
		RETVAL_TRUE;
	}

cleanup:
	if (docids) {
		efree(docids);
	}
	if (vals) {
		efree(vals);
	}
}
/* }}} */
#endif

/* {{{ proto int SphinxClient::__sleep() */
static PHP_METHOD(SphinxClient, __sleep)
{
	php_error_docref(NULL TSRMLS_CC, E_RECOVERABLE_ERROR, "SphinxClient instance cannot be (un)serialized");
}
/* }}} */

/* {{{ proto int SphinxClient::__wakeup() */
static PHP_METHOD(SphinxClient, __wakeup)
{
	php_error_docref(NULL TSRMLS_CC, E_RECOVERABLE_ERROR, "SphinxClient instance cannot be (un)serialized");
}
/* }}} */

/* {{{ arginfo */
ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setserver, 0, 0, 2)
	ZEND_ARG_INFO(0, server)
	ZEND_ARG_INFO(0, port)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setlimits, 0, 0, 2)
	ZEND_ARG_INFO(0, offset)
	ZEND_ARG_INFO(0, limit)
	ZEND_ARG_INFO(0, max_matches)
	ZEND_ARG_INFO(0, cutoff)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setmatchmode, 0, 0, 1)
	ZEND_ARG_INFO(0, mode)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setindexweights, 0, 0, 1)
	ZEND_ARG_INFO(0, weights)
ZEND_END_ARG_INFO()

#if LIBSPHINX_VERSION_ID >= 99
ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setselect, 0, 0, 1)
	ZEND_ARG_INFO(0, clause)
ZEND_END_ARG_INFO()
#endif

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setidrange, 0, 0, 2)
	ZEND_ARG_INFO(0, min)
	ZEND_ARG_INFO(0, max)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setfilter, 0, 0, 2)
	ZEND_ARG_INFO(0, attribute)
	ZEND_ARG_INFO(0, values)
	ZEND_ARG_INFO(0, exclude)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setfilterrange, 0, 0, 3)
	ZEND_ARG_INFO(0, attribute)
	ZEND_ARG_INFO(0, min)
	ZEND_ARG_INFO(0, max)
	ZEND_ARG_INFO(0, exclude)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setgeoanchor, 0, 0, 4)
	ZEND_ARG_INFO(0, attrlat)
	ZEND_ARG_INFO(0, attrlong)
	ZEND_ARG_INFO(0, latitude)
	ZEND_ARG_INFO(0, longitude)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setgroupby, 0, 0, 2)
	ZEND_ARG_INFO(0, attribute)
	ZEND_ARG_INFO(0, func)
	ZEND_ARG_INFO(0, groupsort)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setgroupdistinct, 0, 0, 1)
	ZEND_ARG_INFO(0, attribute)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setretries, 0, 0, 1)
	ZEND_ARG_INFO(0, count)
	ZEND_ARG_INFO(0, delay)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setmaxquerytime, 0, 0, 1)
	ZEND_ARG_INFO(0, qtime)
ZEND_END_ARG_INFO()

#if LIBSPHINX_VERSION_ID >= 99
ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setoverride, 0, 0, 3)
	ZEND_ARG_INFO(0, attribute)
	ZEND_ARG_INFO(0, type)
	ZEND_ARG_INFO(0, values)
ZEND_END_ARG_INFO()
#endif

#if HAVE_3ARG_SPHINX_SET_RANKING_MODE
ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setrankingmode, 0, 0, 1)
	ZEND_ARG_INFO(0, ranker)
	ZEND_ARG_INFO(0, rank_expression)
ZEND_END_ARG_INFO()
#else
ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setrankingmode, 0, 0, 1)
	ZEND_ARG_INFO(0, ranker)
ZEND_END_ARG_INFO()
#endif

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setsortmode, 0, 0, 1)
	ZEND_ARG_INFO(0, mode)
	ZEND_ARG_INFO(0, sortby)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setconnecttimeout, 0, 0, 1)
	ZEND_ARG_INFO(0, timeout)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_setarrayresult, 0, 0, 1)
	ZEND_ARG_INFO(0, array_result)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_updateattributes, 0, 0, 3)
	ZEND_ARG_INFO(0, index)
	ZEND_ARG_INFO(0, attributes)
	ZEND_ARG_INFO(0, values)
	ZEND_ARG_INFO(0, mva)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_buildexcerpts, 0, 0, 3)
	ZEND_ARG_INFO(0, docs)
	ZEND_ARG_INFO(0, index)
	ZEND_ARG_INFO(0, words)
	ZEND_ARG_INFO(0, opts)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_buildkeywords, 0, 0, 3)
	ZEND_ARG_INFO(0, query)
	ZEND_ARG_INFO(0, index)
	ZEND_ARG_INFO(0, hits)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_query, 0, 0, 1)
	ZEND_ARG_INFO(0, query)
	ZEND_ARG_INFO(0, index)
	ZEND_ARG_INFO(0, comment)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO(arginfo_sphinxclient__param_void, 0)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO_EX(arginfo_sphinxclient_escapestring, 0, 0, 1)
	ZEND_ARG_INFO(0, data)
ZEND_END_ARG_INFO()
/* }}} */

static zend_function_entry sphinx_client_methods[] = { /* {{{ */
	PHP_ME(SphinxClient, __construct, 			arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, addQuery, 				arginfo_sphinxclient_query, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, buildExcerpts, 		arginfo_sphinxclient_buildexcerpts, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, buildKeywords, 		arginfo_sphinxclient_buildkeywords, ZEND_ACC_PUBLIC)
#if LIBSPHINX_VERSION_ID >= 99
	PHP_ME(SphinxClient, close, 				arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
#endif		
	PHP_ME(SphinxClient, getLastError, 			arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, getLastWarning, 		arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, escapeString, 			arginfo_sphinxclient_escapestring, ZEND_ACC_PUBLIC)
#if LIBSPHINX_VERSION_ID >= 99
	PHP_ME(SphinxClient, open, 					arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
#endif		
	PHP_ME(SphinxClient, query, 				arginfo_sphinxclient_query, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, resetFilters, 			arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, resetGroupBy, 			arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, runQueries, 			arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setArrayResult, 		arginfo_sphinxclient_setarrayresult, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setConnectTimeout, 	arginfo_sphinxclient_setconnecttimeout, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setFieldWeights, 		arginfo_sphinxclient_setindexweights, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setFilter, 			arginfo_sphinxclient_setfilter, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setFilterFloatRange, 	arginfo_sphinxclient_setfilterrange, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setFilterRange, 		arginfo_sphinxclient_setfilterrange, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setGeoAnchor, 			arginfo_sphinxclient_setgeoanchor, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setGroupBy, 			arginfo_sphinxclient_setgroupby, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setGroupDistinct, 		arginfo_sphinxclient_setgroupdistinct, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setIndexWeights, 		arginfo_sphinxclient_setindexweights, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setIDRange, 			arginfo_sphinxclient_setidrange, ZEND_ACC_PUBLIC)
#if LIBSPHINX_VERSION_ID >= 99
	PHP_ME(SphinxClient, setSelect, 			arginfo_sphinxclient_setselect, ZEND_ACC_PUBLIC)
#endif
	PHP_ME(SphinxClient, setLimits, 			arginfo_sphinxclient_setlimits, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setMatchMode, 			arginfo_sphinxclient_setmatchmode, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setMaxQueryTime, 		arginfo_sphinxclient_setmaxquerytime, ZEND_ACC_PUBLIC)
#if LIBSPHINX_VERSION_ID >= 99
	PHP_ME(SphinxClient, setOverride, 			arginfo_sphinxclient_setoverride, ZEND_ACC_PUBLIC)
#endif	
	PHP_ME(SphinxClient, setRankingMode, 		arginfo_sphinxclient_setrankingmode, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setRetries, 			arginfo_sphinxclient_setretries, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setServer, 			arginfo_sphinxclient_setserver, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, setSortMode, 			arginfo_sphinxclient_setsortmode, ZEND_ACC_PUBLIC)
#if LIBSPHINX_VERSION_ID >= 99
	PHP_ME(SphinxClient, status, 				arginfo_sphinxclient__param_void, ZEND_ACC_PUBLIC)	
#endif	
	PHP_ME(SphinxClient, updateAttributes, 		arginfo_sphinxclient_updateattributes, ZEND_ACC_PUBLIC)
	PHP_ME(SphinxClient, __sleep,				NULL, ZEND_ACC_PUBLIC|ZEND_ACC_FINAL)
	PHP_ME(SphinxClient, __wakeup,				NULL, ZEND_ACC_PUBLIC|ZEND_ACC_FINAL)
	{NULL, NULL, NULL}
};
/* }}} */

/* {{{ PHP_MINIT_FUNCTION
 */
PHP_MINIT_FUNCTION(sphinx)
{
	zend_class_entry ce;

	memcpy(&cannot_be_cloned, zend_get_std_object_handlers(), sizeof(zend_object_handlers));
	cannot_be_cloned.clone_obj = NULL;

	memcpy(&php_sphinx_client_handlers, zend_get_std_object_handlers(), sizeof(zend_object_handlers));
	php_sphinx_client_handlers.clone_obj = NULL;
	php_sphinx_client_handlers.read_property = php_sphinx_client_read_property;
	php_sphinx_client_handlers.get_properties = php_sphinx_client_get_properties;

	INIT_CLASS_ENTRY(ce, "SphinxClient", sphinx_client_methods);
	ce_sphinx_client = zend_register_internal_class(&ce TSRMLS_CC);
	ce_sphinx_client->create_object = php_sphinx_client_new;

	SPHINX_CONST(SEARCHD_OK);
	SPHINX_CONST(SEARCHD_ERROR);
	SPHINX_CONST(SEARCHD_RETRY);
	SPHINX_CONST(SEARCHD_WARNING);
	
	SPHINX_CONST(SPH_MATCH_ALL);
	SPHINX_CONST(SPH_MATCH_ANY);
	SPHINX_CONST(SPH_MATCH_PHRASE);
	SPHINX_CONST(SPH_MATCH_BOOLEAN);
	SPHINX_CONST(SPH_MATCH_EXTENDED);
	SPHINX_CONST(SPH_MATCH_FULLSCAN);
	SPHINX_CONST(SPH_MATCH_EXTENDED2);
	
	SPHINX_CONST(SPH_RANK_PROXIMITY_BM25);
	SPHINX_CONST(SPH_RANK_BM25);
	SPHINX_CONST(SPH_RANK_NONE);
	SPHINX_CONST(SPH_RANK_WORDCOUNT);
#ifdef SPH_RANK_PROXIMITY
	SPHINX_CONST(SPH_RANK_PROXIMITY);
#endif
#ifdef SPH_RANK_MATCHANY
	SPHINX_CONST(SPH_RANK_MATCHANY);
#endif
#ifdef SPH_RANK_FIELDMASK
	SPHINX_CONST(SPH_RANK_FIELDMASK);
#endif
#ifdef SPH_RANK_SPH04
	SPHINX_CONST(SPH_RANK_SPH04);
#endif
#ifdef SPH_RANK_EXPR
	SPHINX_CONST(SPH_RANK_EXPR);
#endif
#ifdef SPH_RANK_TOTAL
	SPHINX_CONST(SPH_RANK_TOTAL);
#endif

	SPHINX_CONST(SPH_SORT_RELEVANCE);
	SPHINX_CONST(SPH_SORT_ATTR_DESC);
	SPHINX_CONST(SPH_SORT_ATTR_ASC);
	SPHINX_CONST(SPH_SORT_TIME_SEGMENTS);
	SPHINX_CONST(SPH_SORT_EXTENDED);
	SPHINX_CONST(SPH_SORT_EXPR);
	
	SPHINX_CONST(SPH_FILTER_VALUES);
	SPHINX_CONST(SPH_FILTER_RANGE);
	SPHINX_CONST(SPH_FILTER_FLOATRANGE);

	SPHINX_CONST(SPH_ATTR_INTEGER);
	SPHINX_CONST(SPH_ATTR_TIMESTAMP);
	SPHINX_CONST(SPH_ATTR_ORDINAL);
	SPHINX_CONST(SPH_ATTR_BOOL);
	SPHINX_CONST(SPH_ATTR_FLOAT);
	SPHINX_CONST(SPH_ATTR_MULTI);
	
	SPHINX_CONST(SPH_GROUPBY_DAY);
	SPHINX_CONST(SPH_GROUPBY_WEEK);
	SPHINX_CONST(SPH_GROUPBY_MONTH);
	SPHINX_CONST(SPH_GROUPBY_YEAR);
	SPHINX_CONST(SPH_GROUPBY_ATTR);
	SPHINX_CONST(SPH_GROUPBY_ATTRPAIR);
	
	return SUCCESS;
}
/* }}} */

/* {{{ PHP_MINFO_FUNCTION
 */
PHP_MINFO_FUNCTION(sphinx)
{
	php_info_print_table_start();
	php_info_print_table_header(2, "sphinx support", "enabled");
	php_info_print_table_header(2, "Version", PHP_SPHINX_VERSION);
	php_info_print_table_header(2, "Revision", "$Revision: 327696 $");
	php_info_print_table_end();
}
/* }}} */

static zend_function_entry sphinx_functions[] = { /* {{{ */
	{NULL, NULL, NULL}
};
/* }}} */

/* {{{ sphinx_module_entry
 */
zend_module_entry sphinx_module_entry = {
#if ZEND_MODULE_API_NO >= 20010901
	STANDARD_MODULE_HEADER,
#endif
	"sphinx",
	sphinx_functions,
	PHP_MINIT(sphinx),
	NULL,
	NULL,
	NULL,
	PHP_MINFO(sphinx),
#if ZEND_MODULE_API_NO >= 20010901
	PHP_SPHINX_VERSION,
#endif
	STANDARD_MODULE_PROPERTIES
};
/* }}} */

/*
 * Local variables:
 * tab-width: 4
 * c-basic-offset: 4
 * End:
 * vim600: noet sw=4 ts=4 fdm=marker
 * vim<600: noet sw=4 ts=4
 */
